#coding:utf-8
#
# id:           bugs.core_2164
# title:        error in operator "and" in as clausule where
# decription:   
# tracker_id:   CORE-2164
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """
    create domain dcodempresa as integer;
    create domain dcadena30 as varchar(30) default '';
    create domain dcod_anuncio as integer;
    create domain dcodmedio as integer;
    create domain dfecha as timestamp;
    create domain dentero as integer;
    create domain dimporte as numeric(10,2);
    commit;

    create table empresas (
        cod_empresa dcodempresa not null,
        nombre dcadena30,
        provincia dcadena30,
        constraint pk_empresas primary key (cod_empresa)
    );

    create table anuncios (
        cod_anuncio dcod_anuncio not null,
        descripcion dcadena30,
        cod_empresa dcodempresa not null,
        constraint pk_anuncios primary key (cod_anuncio)
    );

    create table medios (
        cod_medio dcodmedio not null,
        nombre dcadena30,
        provincia dcadena30,
        constraint pk_medios primary key (cod_medio)
    );

    create table emisiones (
        cod_anuncio dcod_anuncio not null,
        fecha dfecha,
        veces dentero,
        importe dimporte,
        cod_medio dcodmedio not null,
        constraint pk_emisiones primary key (cod_anuncio,cod_medio)
    );


    alter table anuncios add foreign key (cod_empresa) references empresas (cod_empresa) on update cascade on delete no action ;
    alter table emisiones add foreign key (cod_anuncio) references anuncios (cod_anuncio) on update cascade on delete no action ;
    alter table emisiones add foreign key (cod_medio) references medios (cod_medio) on update cascade on delete no action ;
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    --------------------- data script --------------------------------------
    delete from emisiones;
    delete from anuncios;
    delete from empresas;
    delete from medios;
    commit;


    insert into empresas (cod_empresa,nombre,provincia)
                              values (1,'puleva','granada');
    insert into empresas (cod_empresa,nombre,provincia)
                              values (2,'covap','cordoba');
    insert into empresas (cod_empresa,nombre,provincia)
                              values (3,'la vega','malaga');

    insert into medios (cod_medio,nombre,provincia)
                               values (1,'diario sur','malaga');
    insert into medios (cod_medio,nombre,provincia)
                               values (2,'40 granada','granada');
    insert into medios (cod_medio,nombre,provincia)
                               values (3,'el pais','madrid');


    insert into anuncios (cod_anuncio,descripcion,cod_empresa)
                         values (1,'la mejor leche',1);
    insert into anuncios (cod_anuncio,descripcion,cod_empresa)
                         values (2,'la dieta mediterranea ',1);
    insert into anuncios (cod_anuncio,descripcion,cod_empresa)
                         values (3,'el valle de los pedroches',2);


    insert into emisiones (cod_anuncio,fecha,veces,importe,cod_medio)
                             values (1,'10/01/2007',3,25,1);
    insert into emisiones (cod_anuncio,fecha,veces,importe,cod_medio)
                             values (1,'10/11/2007',3,25,3);
    insert into emisiones (cod_anuncio,fecha,veces,importe,cod_medio)
                             values (1,'10/01/2007',4,30,2);
    insert into emisiones (cod_anuncio,fecha,veces,importe,cod_medio)
                             values (3,'11/01/2007',1,45,3);
    commit;

    -----------------------------------------------------------------

    set list on;
    set count on;
    select e.nombre,a.cod_anuncio
            from empresas e
                 inner join anuncios a on (a.cod_empresa=e.cod_empresa)
            where a.cod_anuncio not in
                          (select em.cod_anuncio
                                        from emisiones em
                                             inner join medios m on (m.cod_medio=em.cod_medio)
                                        where m.provincia<>e.provincia
                          );

    --This statement don't return any rows
    --
    --If append other subselect, it returns one row ?why?
    --The second statement is

    select e.nombre,a.cod_anuncio
            from empresas e
                 inner join anuncios a on (a.cod_empresa=e.cod_empresa)
            where a.cod_anuncio not in
                          (select em.cod_anuncio
                                        from emisiones em
                                             inner join medios m on (m.cod_medio=em.cod_medio)
                                        where m.provincia<>e.provincia
                          )
                  and ------ fails
                  a.cod_anuncio in
                          (select em1.cod_anuncio
                                        from emisiones em1
                                             inner join medios m1 on (m1.cod_medio=em1.cod_medio)
                                        where m1.provincia=e.provincia
                          );

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    NOMBRE                          puleva
    COD_ANUNCIO                     2
    Records affected: 1
    Records affected: 0
  """

@pytest.mark.version('>=2.5')
def test_core_2164_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

