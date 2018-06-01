---
typora-copy-images-to: ./report pic
---

# Car

> Author: Shihan Ran, 15307130424

## Problem 1: Warmup

### 1a. Question

Suppose we have a sensor reading for the second timestep, $D_2=0$. Compute the posterior distribution $P(C_2=1\mid D_2=0)$.

### 1a. Answer

Here's what the Bayesian network (it's an HMM, in fact) looks like:

![image-20180530170340936](/Users/ranshihan/Coding/FDU-Artificial-Intelligence/Projects/PJ4 - Car/report pic/image-20180530170340936.png)

So the posterior distribution can be computed like following:
$$
\begin{aligned}
P(C_2=1\mid D_2=0)&=\frac{P(C_2=1, D_2=0)}{P(D_2=0)}\\
&=\frac{P(D_2=0\mid C_2=1)*P(C_2=1)}{P(D_2=0)}\\
&=\frac{P(D_2=0\mid C_2=1)*P(C_2=1)}{\sum_{C_2} P(D_2=0\mid C_2)P(C_2)}\\
&=\frac{P(D_2=0\mid C_2=1)*\big[\sum_{C_1} P(C_2=1\mid C_1)P(C_1)\big]}{\sum_{C_2} P(D_2=0\mid C_2)P(C_2)}\\
&=\frac{\eta * \big[\epsilon*0.5+(1-\epsilon)*0.5\big]}{(1-\eta)*[\epsilon*0.5+(1-\epsilon)*0.5\big]+\eta*[\epsilon*0.5+(1-\epsilon)*0.5\big]}\\
&=\frac{\eta*0.5}{0.5}\\
&=\eta
\end{aligned}
$$

### 1b. Question

Suppose a time step has elapsed and we got another sensor reading $D_3=1$, but we are still interested in $C_2$. Compute the posterior distribution $P(C_2=1\mid D_2=0, D_3=1)$.

### 1b. Answer

$$
\begin{aligned}
P(C_2\mid D_2=0, D_3=1)&\propto \sum_{C_1, C_3}P(C_1)P(C_2\mid C_1)P(D_2=0\mid C_2) P(C_3\mid C_2)P(D_3=1\mid C_3)\\
&\propto P(D_2=0\mid C_2)\big[\sum_{C_1}P(C_1)P(C_2\mid C_1)\big]\big[\sum_{C_3}P(C_3\mid C_2)P(D_3=1\mid C_3)\big]\\\\
P(C_2=1\mid D_2=0, D_3=1)&\propto \eta\big[0.5(\epsilon+1-\epsilon)\big]\big[(1-\epsilon)(1-\eta)+\epsilon\eta\big]\\
P(C_2=0\mid D_2=0, D_3=1)&\propto (1-\eta)\big[0.5(\epsilon+1-\epsilon)\big]\big[(1-\epsilon)\eta+\epsilon(1-\eta)\big]\\\\
P(C_2=1\mid D_2=0, D_3=1)&=\frac{P(C_2=1\mid D_2=0, D_3=1)}{P(C_2=1\mid D_2=0, D_3=1)+P(C_2=0\mid D_2=0, D_3=1)}\\
&=\frac{\eta\big[(1-\epsilon)(1-\eta)+\epsilon\eta\big]}{\eta\big[(1-\epsilon)(1-\eta)+\epsilon\eta\big]+(1-\eta)\big[(1-\epsilon)\eta+\epsilon(1-\eta)\big]}
\end{aligned}
$$

### 1c. Question

![image-20180530175023084](/Users/ranshihan/Coding/FDU-Artificial-Intelligence/Projects/PJ4 - Car/report pic/image-20180530175023084.png)

### 1c. Answer

#### i.

$$
P(C_2=1\mid D_2=0)=\eta=0.2000\\
P(C_2=1\mid D_2=0, D_3=1)=0.4157
$$

#### ii.

From our results, we know $P(C_2=1\mid D_2=0) < P(C_2=1\mid D_2=0, D_3=1)$. We can draw the conclusion that adding the second sensor $D_3=1$ increased the probability of $P(C_2)=1$. The position of a car observed at time step $t$ is also related to the position of the car at time step $t+1$. So the observation of $D_3=1$ increased the probability of $C_2=1$.

#### iii.

Set $\epsilon=0$. Hence $P(C_t\mid C_{t-1})=1, when\,C_t=C_{t-1}$. Thus the value of $D_3$ is only related to $D_3$ with parameter $\eta$, and we don't need to consider the transition probability of $P(C_3\mid C_2)$.

You can also derive the above conclusion from the formula.

## PROBLEM 2: Emission probabilities

### 2a. Check my Code.

## PROBLEM 3: Transition probabilities 

### 3a. Check my Code.

## PROBLEM 4: LEARNING TO PLAY BLACKJACK

### 4a. Check my Code.

### 4b. Question

Call *simulate()* using your algorithm and the *identityFeatureExtractor()* on the MDP *smallMDP*, with 30000 trials. Compare the policy learned in this case to the policy learned by value iteration. Don't forget to set the explorationProb of your Q-learning algorithm to 0 after learning the policy. How do the two policies compare (i.e., for how many states do they produce a different action)? Now run *simulate()* on *largeMDP*. How does the policy learned in this case compare to the policy learned by value iteration? What went wrong? 

### 4b. Answer

|                                              | Small MDP                                                    | Large MDP                                                    |
| -------------------------------------------- | :----------------------------------------------------------- | ------------------------------------------------------------ |
| Value Iteration                              | 5                                                            | 15                                                           |
| Intersection probabilitiy between 2 policies | 0.74                                                         | 0.67                                                         |
| Reasons                                      | Since the relatively small state space allows Q­learning algorithm to learn the Q values better, Q­learning does better than value iteration. | Since the state space is much lager, which make Q­learning algorithm not capable of learning accurate Q values. Also, our implemented *identityFeatureExtractor* can only return a singleton list containing indicator feature for the (state, action) pair and it provides no generalization. |

### 4c. Check my Code.

### 4d. Question

Now let's explore the way in which value iteration responds to a change in the rules of the MDP. Run value iteration on originalMDP to compute an optimal policy. Then apply your policy to newThresholdMDP by calling simulate with FixedRLAlgorithm, instantiated using your computed policy. What reward do you get? What happens if you run Q learning on newThresholdMDP instead? Explain. 

### 4d. Answer

I get relatively low sum rewards **205393** for FixedRLAlgorithm because I passed the policy learned for originalMDP in it. Since FixedRLAlgorithm can not adapt, the actions taken are not optimal actions for newThresholdMDP. 

Q­learning has higher sum rewards **360000** because it is able to adapt to newThresholdMDP. 
