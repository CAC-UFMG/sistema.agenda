Instalação
==========

1. Instalar o git
2. cd ... Plone/zinstance/src (ou  ... Plone/zeoserver/src)
3. git clone https://github.com/CAC-UFMG/sistema.agenda.git


Atualização na máquina
=======================
git pull


Atualização no repositório
===========================
1.mudar arquivo
2.git add -p
3.git commit -a
4.git push 


Instalação do agendamento
=========================
1. colocar sistema.agenda no buildout em development e eggs
2. rodar o buildout
3. iniciar o servidor

usuário: agendador
senha: agendador


Inserir 

environment-vars =
        TZ America/Sao_Paulo
		
Em buildout.cfg na seção [instance]