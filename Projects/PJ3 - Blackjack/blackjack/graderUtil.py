# Library to do grading of Python programs.
# Percy Liang
#
# Usage:
#   # create a grader
#   grader = Grader("Name of assignment")
#   # add a basic test (which is visible to students)
#   grader.addBasicPart(name, gradeFunc, maxPoints, maxSeconds, description="a basic test")
#   # add a hidden test (MUST be in BEGIN_HIDDEN block)
#   grader.addHiddenPart(name, gradeFunc, maxPoints, maxSeconds, description="a hidden test")
#   # add a manual grading part
#   grader.addManualPart(name, gradeFunc, maxPoints, description="written problem 3c")
#   # run grading
#   grader.grade()

import datetime, math, pprint, traceback, sys, signal, os, json
import gc

defaultMaxSeconds = 5  # 5 second
TOLERANCE = 1e-4  # For measuring whether two floats are equal

BASIC_MODE = 'basic'
ALL_MODE = 'auto'

# When reporting stack traces as feedback, ignore parts specific to the grading
# system.
def isTracebackItemGrader(item):
    return item[0].endswith('graderUtil.py')

def isCollection(x):
    return isinstance(x, list) or isinstance(x, tuple)

def dumpYamlOrPprint(x, out):
    try:
        import yaml
        haveYaml = True
    except ImportError:
        yaml = None
        haveYaml = False

    if haveYaml:
        yaml.dump(x, out)
    else:
        pprint.pprint(x, stream=out)

# Return whether two answers are equal.
def isEqual(trueAnswer, predAnswer, tolerance = TOLERANCE):
    # Handle floats specially
    if isinstance(trueAnswer, float) or isinstance(predAnswer, float):
        return abs(trueAnswer - predAnswer) < tolerance
    # Recurse on collections to deal with floats inside them
    if isCollection(trueAnswer) and isCollection(predAnswer) and len(trueAnswer) == len(predAnswer):
        for a, b in zip(trueAnswer, predAnswer):
            if not isEqual(a, b): return False
        return True
    if isinstance(trueAnswer, dict) and isinstance(predAnswer, dict):
        if len(trueAnswer) != len(predAnswer): return False
        for k, v in trueAnswer.items():
            if not isEqual(predAnswer.get(k), v): return False
        return True

    # Numpy array comparison
    if type(trueAnswer).__name__=='ndarray':
        import numpy as np
        if isinstance(trueAnswer, np.ndarray) and isinstance(predAnswer, np.ndarray):
            if trueAnswer.shape != predAnswer.shape:
                return False
            for a, b in zip(trueAnswer, predAnswer):
                if not isEqual(a, b): return False
            return True

    # Do normal comparison
    return trueAnswer == predAnswer

# Run a function, timing out after maxSeconds.
class TimeoutFunctionException(Exception): pass
class TimeoutFunction:
    def __init__(self, function, maxSeconds):
        self.maxSeconds = maxSeconds
        self.function = function

    def handle_maxSeconds(self, signum, frame):
        print 'TIMEOUT!'
        raise TimeoutFunctionException()

    def __call__(self, *args):
        if os.name == 'nt':
            # Windows does not have signal.SIGALRM
            # Will not stop after maxSeconds second but can still throw an exception
            timeStart = datetime.datetime.now()
            result = self.function(*args)
            timeEnd = datetime.datetime.now()
            if timeEnd - timeStart > datetime.timedelta(seconds=self.maxSeconds + 1):
                raise TimeoutFunctionException()
            return result
            # End modification for Windows here
        old = signal.signal(signal.SIGALRM, self.handle_maxSeconds)
        signal.alarm(self.maxSeconds + 1)
        result = self.function(*args)
        signal.alarm(0)
        return result

class Part:
    def __init__(self, name, gradeFunc, maxPoints, maxSeconds, extraCredit, description):
        if not isinstance(name, str): raise Exception("Invalid name: %s" % name)
        if gradeFunc != None and not callable(gradeFunc): raise Exception("Invalid gradeFunc: %s" % gradeFunc)
        if not isinstance(maxPoints, int): raise Exception("Invalid maxPoints: %s" % maxPoints)
        if maxSeconds != None and not isinstance(maxSeconds, int): raise Exception("Invalid maxSeconds: %s" % maxSeconds)
        # Specification
        self.name = name
        self.gradeFunc = gradeFunc  # Function to call to do grading
        self.maxPoints = maxPoints  # Maximum number of points attainable on this part
        self.maxSeconds = maxSeconds  # Maximum allowed time that the student's code can take (in seconds)
        self.extraCredit = extraCredit  # Whether this is an extra credit problem
        self.description = description  # Description of this part
        self.basic = False  # Can be changed
        # Statistics
        self.points = 0
        self.seconds = 0
        self.messages = []
        self.failed = False

    def fail(self):
        self.failed = True

def checkValidAssignmentId(assnId):
    if os.path.exists('submit.conf'):
        import yaml
        with open('submit.conf', 'r') as submit_conf:
            info = yaml.load(submit_conf)
        assignmentIds = set([assign['id'] for assign in info['assignments']])
        if not assnId in assignmentIds:
            raise ValueError('Assignment ID %s not valid according to submit.conf' % assnId)

class Grader:
    def __init__(self, args=sys.argv):
        self.parts = []  # Auto parts (to be added)
        self.manualParts = []  # Manual parts (to be added)
        self.selectedPartName = None  # Part name to grade
        self.useSolution = False

        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument('--js', action='store_true', help='Write JS instead of YAML')
        parser.add_argument('--summary', action='store_true', help='Don\'t actually run code, just print out')
        parser.add_argument('--assignmentId', help='assignmentId (used to read information)')
        parser.add_argument('remainder', nargs=argparse.REMAINDER)
        self.params = parser.parse_args(args[1:])

        args = self.params.remainder
        if len(args) < 1:
            self.mode = ALL_MODE
        else:
            if args[0] in [BASIC_MODE, ALL_MODE]:
                self.mode = args[0]
            else:
                self.mode = ALL_MODE
                self.selectedPartName = args[0]

        if self.params.assignmentId is not None:
            checkValidAssignmentId(self.params.assignmentId)

        self.messages = []  # General messages
        self.currentPart = None  # Which part we're grading
        self.fatalError = False  # Set this if we should just stop immediately

    def addBasicPart(self, name, gradeFunc, maxPoints=1, maxSeconds=defaultMaxSeconds, description=""):
        """Add a basic test case. The test will be visible to students."""
        if not self.isSelected(name): return
        part = Part(name, gradeFunc, maxPoints, maxSeconds, False, description)
        part.basic = True
        self.parts.append(part)

    def addHiddenPart(self, name, gradeFunc, maxPoints=1, maxSeconds=defaultMaxSeconds, extraCredit=False, description=""):
        """Add a hidden test case. The test should NOT be visible to students
        so should be inside a BEGIN_HIDE block."""
        if not self.isSelected(name): return
        if name in [part.name for part in self.parts]:
            raise Exception("Part name %s already exists" % name)
        part = Part(name, gradeFunc, maxPoints, maxSeconds, extraCredit, description)
        self.parts.append(part)

    def addManualPart(self, name, maxPoints, extraCredit=False, description=""):
        """Add stub for a part to be manually graded."""
        if not self.isSelected(name): return
        part = Part(name, None, maxPoints, None, extraCredit, description)
        self.manualParts.append(part)

    def isSelected(self, partName):
        return self.selectedPartName == None or self.selectedPartName == partName

    # Try to load the module (submission from student).
    def load(self, moduleName):
        try:
            return __import__(moduleName)
        except Exception, e:
            self.fail("Threw exception when importing '%s': %s" % (moduleName, e))
            self.fatalError = True
            return None
        except:
            self.fail("Threw exception when importing '%s'" % moduleName)
            self.fatalError = True
            return None

    def grade(self):
        print '========== START GRADING'
        if self.mode == ALL_MODE:
            parts = self.parts
        else:
            parts = [part for part in self.parts if part.basic]
        for part in parts:
            if self.fatalError: continue
            if self.params.summary: continue

            print '----- START PART %s' % part.name
            self.currentPart = part

            startTime = datetime.datetime.now()
            try:
                TimeoutFunction(part.gradeFunc, part.maxSeconds)()  # Call the part's function
            except KeyboardInterrupt:
                raise
            except TimeoutFunctionException as e:
                self.fail('Time limit (%s seconds) exceeded.' % part.maxSeconds)
            except MemoryError as e:
                gc.collect()
                self.fail('Memory limit exceeded.')
            except Exception as e:
                self.fail('Exception thrown: %s -- %s' % (str(type(e)), str(e)))
                self.printException()
            except SystemExit as e:
                # Catch SystemExit raised by exit(), quit() or sys.exit()
                # This class is not a subclass of Exception and we don't
                # expect students to raise it.
                self.fail('Unexpected exit.')
                self.printException()
            endTime = datetime.datetime.now()
            part.seconds = (endTime - startTime).seconds
            if not self.useSolution and not part.basic:
                displayPoints = '--'
            else:
                displayPoints = part.points
            print '----- END PART %s [took %s (max %s seconds), %s/%s points]' % (part.name, endTime - startTime, part.maxSeconds, displayPoints, part.maxPoints)

        totalPoints = sum(part.points for part in parts)
        maxGradedPoints = sum(part.maxPoints for part in parts if self.useSolution or part.basic)
        maxTotalPoints = sum(part.maxPoints for part in parts)
        if not self.useSolution:
            print 'Note that the hidden test cases do not check for correctness.' \
            '\nThey are provided for you to verify that the functions do not crash and run within the time limit.' \
            '\nPoints for these parts not assigned by the grader (indicated by "--").'
        print '========== END GRADING [%d/%d points graded]' % (totalPoints, maxGradedPoints)

        try:
            import dateutil.parser
            haveDateutil = True
        except ImportError:
            haveDateutil = False

        # Compute late days (need assignmentId to read dueDate out of submit.conf)
        lateDays = None
        if os.path.exists('metadata') and os.path.exists('submit.conf') and self.params.assignmentId is not None:
            try: 
                timestamp = yaml.load(open('metadata'))['time']
                timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
            except:
                # This might be better to do anyway
                timestamp = datetime.datetime.fromtimestamp(os.path.getctime('metadata'))
            with open('submit.conf', 'r') as submit_conf:
                import yaml
                info = yaml.load(submit_conf)
            dueDate = [
                assign['dueDate']
                for assign in info['assignments']
                if assign['id'] == self.params.assignmentId
            ][0]
            dueDate = dateutil.parser.parse(dueDate)
            # HACK: Fix to choose the end of the day
            dueDate = dueDate.replace(hour = 23, minute = 59)
            if timestamp > dueDate:
                diff = timestamp - dueDate
                lateDays = int(math.ceil(diff.days + diff.seconds / (3600.0 * 24.0)))
            else:
                lateDays = 0

        result = {}
        result['fatalError'] = self.fatalError
        result['mode'] = self.mode
        result['totalPoints'] = totalPoints
        result['maxTotalPoints'] = maxTotalPoints
        result['messages'] = self.messages
        if lateDays is not None:
            result['lateDays'] = lateDays
        resultParts = []
        for part in parts:
            r = {}
            r['name'] = part.name
            r['points'] = part.points
            r['maxPoints'] = part.maxPoints
            r['seconds'] = part.seconds
            r['maxSeconds'] = part.maxSeconds
            r['extraCredit'] = part.extraCredit
            r['messages'] = part.messages
            r['description'] = part.description
            resultParts.append(r)
        result['parts'] = resultParts

        self.output(self.mode, result)

        # Only create if doesn't exist (be careful not to overwrite the manual!)
        if len(self.manualParts) > 0:
            if not os.path.exists(self.getOutputPath('manual')):
                print "Writing %d manual parts to 'grader-manual.out'" % len(self.manualParts)
                result = {}
                resultParts = []
                for part in self.manualParts:
                    r = {}
                    r['name'] = part.name
                    # Let the question marks be filled in later
                    r['points'] = '?'
                    r['maxPoints'] = part.maxPoints
                    r['extraCredit'] = part.extraCredit
                    r['messages'] = ['?']
                    r['description'] = part.description
                    resultParts.append(r)
                result['parts'] = resultParts
                self.output('manual', result)
            else:
                pass
        print "Total max points: %d" % (maxTotalPoints + sum(part.maxPoints for part in self.manualParts))

    def getOutputPath(self, mode):
        if self.params.js:
            return 'grader-%s.js' % mode
        else:
            return 'grader-%s.out' % mode

    def output(self, mode, result):
        path = self.getOutputPath(mode)
        if self.params.js:
            with open(path, 'w') as out:
                print >>out, 'var ' + mode + 'Result = '+ json.dumps(result) + ';'
        else:
            path = 'grader-%s.out' % mode
            with open(path, 'w') as out:
                dumpYamlOrPprint(result, out)
        print 'Wrote results to %s' % path


    # Called by the grader to modify state of the current part

    def assignFullCredit(self):
        if not self.currentPart.failed:
            self.currentPart.points = self.currentPart.maxPoints
        return True
        
    def assignPartialCredit(self, credit):
        self.currentPart.points = credit
        return True;

    def requireIsValidPdf(self, path):
        if not os.path.exists(path):
            return self.fail("File '%s' does not exist" % path)
        if os.path.getsize(path) == 0:
            return self.fail("File '%s' is empty" % path)
        if os.name == 'nt':
            # Windows does not have the `file` command
            # Use very, very basic check
            try:
                with open(path, 'rb') as fin:
                    if fin.read(4) != '%PDF':
                        return self.fail("File '%s' does not look like a PDF file." % path)
            except Exception, e:
                return self.fail("File '%s' cannot be opened: %s" % (path, e))
        else:
            fileType = os.popen('file %s' % path).read()
            if 'PDF document' not in fileType:
                return self.fail("File '%s' is not a PDF file: %s" % (path, fileType))
        return self.assignFullCredit()

    def requireIsNumeric(self, answer):
        if isinstance(answer, int) or isinstance(answer, float):
            return self.assignFullCredit()
        else:
            return self.fail("Expected either int or float, but got '%s'" % answer)

    def requireIsOneOf(self, trueAnswers, predAnswer):
        if predAnswer in trueAnswers:
            return self.assignFullCredit()
        else:
            return self.fail("Expected one of %s, but got '%s'" % (trueAnswers, predAnswer))

    def requireIsEqual(self, trueAnswer, predAnswer, tolerance = TOLERANCE):
        if isEqual(trueAnswer, predAnswer, tolerance):
            return self.assignFullCredit()
        else:
            return self.fail("Expected '%s', but got '%s'" % (str(trueAnswer), str(predAnswer)))

    def requireIsLessThan(self, lessThanQuantity, predAnswer ):
        if predAnswer < lessThanQuantity:
            return self.assignFullCredit()
        else:
            return self.fail("Expected to be < %f, but got %f" % (lessThanQuantity, predAnswer) )

    def requireIsGreaterThan(self, greaterThanQuantity, predAnswer ):
        if predAnswer > greaterThanQuantity:
            return self.assignFullCredit()
        else:
            return self.fail("Expected to be > %f, but got %f" %
                    (greaterThanQuantity, predAnswer) )

    def requireIsTrue(self, predAnswer):
        if predAnswer:
            return self.assignFullCredit()
        else:
            return self.fail("Expected to be true, but got false" )

    def fail(self, message):
        self.addMessage(message)
        if self.currentPart:
            self.currentPart.points = 0
            self.currentPart.fail()
        return False

    def printException(self):
        tb = [item for item in traceback.extract_tb(sys.exc_traceback) if not isTracebackItemGrader(item)]
        for item in traceback.format_list(tb):
            self.fail('%s' % item)

    def addMessage(self, message):
        if not self.useSolution:
            print message
        if self.currentPart:
            self.currentPart.messages.append(message)
        else:
            self.messages.append(message)
