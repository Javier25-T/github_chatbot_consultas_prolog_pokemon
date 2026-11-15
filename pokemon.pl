% Base de conocimiento Pokémon - primera generación.


agua(P) :- member(P,[squirtle,wartortle,blastoise,psyduck,golduck,poliwag,poliwhirl,poliwrath,tentacool,tentacruel,slowpoke,slowbro,seel,dewgong,shellder,cloyster,krabby,kingler,horsea,seadra,goldeen,seaking,staryu,starmie,magikarp,gyarados,lapras,vaporeon,omanyte,omastar,kabuto,kabutops]).
bicho(P) :- member(P,[caterpie,metapod,butterfree,weedle,kakuna,beedrill,paras,parasect,venonat,venomoth,pinsir,scyther]).
dragon(P) :- member(P,[dratini,dragonair,dragonite]).
electrico(P) :- member(P,[pikachu,raichu,magnemite,magneton,voltorb,electrode,electabuzz,jolteon,zapdos]).
fantasma(P) :- member(P,[gastly,haunter,gengar]).
fuego(P) :- member(P,[charmander,charmeleon,charizard,vulpix,ninetales,growlithe,arcanine,ponyta,rapidash,magmar,flareon,moltres]).
hada(P) :- member(P,[clefairy,clefable,jigglypuff,wigglytuff,mr_mime]).
hielo(P) :- member(P,[dewgong,cloyster,jynx,lapras,articuno]).
lucha(P) :- member(P,[mankey,primeape,poliwrath,machop,machoke,machamp,hitmonlee,hitmonchan]).
metal(P) :- member(P,[magnemite,magneton]).
normal(P) :- member(P,[rattata,raticate,meowth,persian,lickitung,chansey,kangaskhan,tauros,ditto,eevee,porygon,snorlax,jigglypuff,wigglytuff,pidgey,pidgeotto,pidgeot,spearow,fearow,farfetchd,doduo,dodrio]).
planta(P) :- member(P,[paras,parasect,tangela,exeggcute,exeggutor,bulbasaur,ivysaur,venusaur,oddish,gloom,vileplume,bellsprout,weepinbell,victreebel]).
psiquico(P) :- member(P,[abra,kadabra,alakazam,slowpoke,slowbro,drowzee,hypno,exeggcute,exeggutor,starmie,mr_mime,jynx,mewtwo,mew]).
roca(P) :- member(P,[omanyte,omastar,kabuto,kabutops,geodude,graveler,golem,onix,aerodactyl,rhyhorn,rhydon]).
tierra(P) :- member(P,[sandshrew,sandslash,nidoqueen,nidoking,diglett,dugtrio,geodude,graveler,golem,onix,cubone,marowak,rhyhorn,rhydon]).
veneno(P) :- member(P,[bulbasaur,ivysaur,venusaur,weedle,kakuna,beedrill,ekans,arbok,nidoran_f,nidorina,nidoqueen,nidoran_m,nidorino,nidoking,zubat,golbat,oddish,gloom,vileplume,venonat,venomoth,bellsprout,weepinbell,victreebel,tentacool,tentacruel,grimer,muk,gastly,haunter,gengar,koffing,weezing]).
volador(P) :- member(P,[charizard,butterfree,pidgey,pidgeotto,pidgeot,spearow,fearow,zubat,golbat,farfetchd,doduo,dodrio,scyther,gyarados,aerodactyl,articuno,zapdos,moltres,dragonite]).

% Predicado puente: conecta los tipos individuales definidos arriba con la regla general "tipo(Pokemon, Tipo)"
tipo(P,agua) :- agua(P).
tipo(P,bicho) :- bicho(P).
tipo(P,dragon) :- dragon(P).
tipo(P,electrico) :- electrico(P).
tipo(P,fantasma) :- fantasma(P).
tipo(P,fuego) :- fuego(P).
tipo(P,hada) :- hada(P).
tipo(P,hielo) :- hielo(P).
tipo(P,lucha) :- lucha(P).
tipo(P,metal) :- metal(P).
tipo(P,normal) :- normal(P).
tipo(P,planta) :- planta(P).
tipo(P,psiquico) :- psiquico(P).
tipo(P,roca) :- roca(P).
tipo(P,tierra) :- tierra(P).
tipo(P,veneno) :- veneno(P).
tipo(P,volador) :- volador(P).

% ventaja de tipos
tipo_gana(agua,T) :- member(T,[fuego,tierra,roca]).
tipo_gana(fuego,T) :- member(T,[planta,bicho,hielo,metal]).
tipo_gana(planta,T) :- member(T,[tierra,roca,agua]).
tipo_gana(electrico,T) :- member(T,[volador,agua]).
tipo_gana(dragon,T) :- member(T,[fuego,electrico,agua,planta]).
tipo_gana(hielo,T) :- member(T,[dragon,volador,planta,tierra]).
tipo_gana(tierra,T) :- member(T,[electrico,roca,fuego,metal]).
tipo_gana(roca,T) :- member(T,[volador,fuego,bicho,hielo]).
tipo_gana(metal,T) :- member(T,[roca,hielo,hada,veneno]).
tipo_gana(lucha,T) :- member(T,[roca,hielo,metal,normal]).
tipo_gana(psiquico,T) :- member(T,[lucha,veneno]).
tipo_gana(veneno,T) :- member(T,[planta,hada,lucha]).
tipo_gana(volador,T) :- member(T,[planta,bicho,lucha]).
tipo_gana(fantasma,T) :- member(T,[psiquico,lucha]).
tipo_gana(hada,T) :- member(T,[lucha,dragon]).
tipo_gana(bicho,T) :- member(T,[planta,psiquico]).

% Reglas de combate.

gana(X, Y) :-
	tipo(X, TipoX),
	tipo(Y, TipoY),
	tipo_gana(TipoX, TipoY),
	X \= Y.

pierde(X,Y) :-
	gana(Y, X),
	X \= Y.

empata(X,Y) :-
	\+ gana(X,Y),
	\+ pierde(X,Y),
	Y \= X.

/* Ejemplos de consultas.
 * 
 * Squirtle le gana a Charmander?
 * gana(squirtle, charmander).
 * 
 * Qué pokemon le ganan a Pikachu?
 * setof(P, gana(P, pikachu), ListaVencedores).
 * 
 * Qué pokemon le ganan a Charizard?
 * setof(P, pierde(P, charizard), ListaVencedores).
 * 
 * Qué pokemon le ganan a Charizard sin que Charizard pueda ganarle a ellos?
 * gana(X, charizard), \+ gana(charizard, X).
 * 
 * Relaciones 3-cíclicas.
 * gana(X, Y), gana(Y, Z), gana(Z, X), X \= Y, Y \= Z, X \= Z.
 * 
 * Qué pokemon son de tipo agua y hielo?
 * tipo(P, agua), tipo(P, hielo).
 * 
 * Qué pokemon tienen exactamente dos tipos distintos?
 * tipo(P, Tipo1), tipo(P, Tipo2), Tipo1 \= Tipo2.
 * 
 * Cuántos y cuáles pokemon le ganan a Dragonite?
 * list_to_set elimina duplicados, _ListaInicial es variable temporal por el _ al principio.
 * findall(P, gana(P, dragonite), _ListaInicial), list_to_set(_ListaInicial, Lista), length(Lista, Cantidad).
*/