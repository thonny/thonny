#!/usr/bin/bash

_args=("$@") # All parameters from terminal.

_pwd=$(pwd)
[[ ${_pwd} == */thonny/locale ]] && cd ../..

compile_mo(){
    pybabel compile -d thonny/locale/ -D thonny
}

extract_pot(){
    pybabel extract thonny/ --keywords=tr --output-file thonny/locale/thonny.pot
}

update_po(){
    pybabel update -D thonny -i thonny/locale/thonny.pot -d thonny/locale/
}

extract_update(){
    extract_pot;
    update_po;
}

cmo(){      compile_mo;     }
epot(){     extract_pot;    }
upo(){      update_po;      }

eu(){       extract_update; }

${_args[0]}

cd ${_pwd}