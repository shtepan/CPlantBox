Vazeny ctenari,  
&nbsp;&nbsp;&nbsp;nize jsou poznamky k instalaci CPlantBox na Linux - CentOS 7.

Nejprve jsme pracovali v **CRootBox**, kde jsme zjistili, ze vyvoj byl na podzim 2019 prenesen na **CPlantBox**, nejspis ve fazi posunu od **boost-python** k **[pybind11](https://pybind11.readthedocs.io/en/stable/benchmark.html)** napojeni na C++.

Dulezite je zminit, ze CPlantBox vyzaduje alespon *python3.7*. Proto jsme kompilovali ve virtualnim prostredi ```anaconda3-2020.02``` (*python3.7.6*) spoustenem navic pres aplikaci ```pyenv```. Balik Anaconda3 lze snadno nainstalovat prikazem

    pyenv install anaconda3-2020.02

Dostupne verze Python distribuci zobrazi prikaz

    pyenv install -l

CPlantBox jsme stahli pomoci BASH prikazu ```git clone``` z https://github.com/Plant-Root-Soil-Interactions-Modelling/CPlantBox.git

Pri prvni casti kompilace CPlantBox prikazem ```cmake .``` jsme zjistili, ze se nedohledali nektere casti pythonu a proto jsme doplnili na radku 236 (resp. 180 v CRootBoxu) tyto paths do CMakeCache.txt

    //Path to a program.
    PYTHON_EXECUTABLE:FILEPATH=/home/rootlabadmin/.pyenv/shims/python3.7

    //Path to a file.
    PYTHON_INCLUDE_DIR:PATH=/home/rootlabadmin/.pyenv/versions/anaconda3-2020.02/include/python3.7m

    //Path to a library.
    PYTHON_LIBRARY:FILEPATH=/home/rootlabadmin/.pyenv/versions/anaconda3-2020.02/lib/libpython3.7m.a

V CPlantBox uz se pak ```make``` zkompiloval bez problemu.

(V CRootBoxu jeste vznikala odpoved, ze nemuze nalezt python3, ale to bylo zpusobene spatne zapsanou podminkou v CRootBox/src/CMakeLists.txt, opraveno, ```if (PYTHONLIBS_FOUND) # CaseSensitive, CamelCase did not work```. Dale nenachazel Libraries boost_python37, CentOS ma v repos Boost version 1.53 jako nejnovejsi. Napojeni pres boost_python37 jsme dale neladili. Proto po kompilaci nefungoval ```import py_crootbox```.)
