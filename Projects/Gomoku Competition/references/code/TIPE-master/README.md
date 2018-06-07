# TIPE

C'est mon TIPE pour l'année 2017 - 2018 sur le morpion.

Les codes sont dans le fichier "ing"

--------------------------Tic-Tac-Toe-------------------------------------
Cette partie est écrite en Ocaml (Il n'y a pas encore de graphique)

evalue Lv1 		-> evaluer la note d'une position avec une fonction simple

evalue Lv2		-> avec l'arbre, qui est plus intelligente en général.

Si vous voulez changer le code, aller vers 

1. allez vers TIPE/ing/tic-tac-toe/
2. ocamlc -c base.ml
3. ocamlc base.cmo (the file with .ml que vous avez changé) -o "Le nom de ce programme"

----------------------------Gomoku----------------------------------------
Cette intelligence artificialle peut jouer avec le manager suivant:

http://petr.lastovicka.sweb.cz/games.html#piskvorky - Piskvork 8.0.2 - piskvork.zip

Si vous voulez changer le code, vous pouvez:

1. Install Windows (or Wine for Linux, originally the project was created and tested on Ubuntu 16.04 using Wine)
2. Install Python (the code and also following instructions are for version 2.7).
3. Install pywin32 Python package: C:\Python27\Scripts\pip.exe install pypiwin32 (if not present "by default")
4. Install PyInstaller: C:\Python27\Scripts\pip.exe install pyinstaller

Le document .py peut être utilisé avec les commandes suivantes:

cd C:\path\where\the\files\were\saved

C:\Python27\Scripts\pyinstaller.exe pbrain-pengvX.Y.py pisqpipe.py --name pbrain-pyrandom.exe --onefile
--------------------------------------------------------------------------


Pour plus d'information, vous pouvez aller vers les sites:
1. https://github.com/stranskyjan/pbrain-pyrandom
2. http://gomocup.org/category/news/
