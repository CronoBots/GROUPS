-- LA STEP EST UN RECYCLAGE (le client, le 25/10/2026 : « oui, la STEP est
-- un recyclage pour certains opérateurs »). La fiche de recyclage ne
-- connaissait que les cinq ateliers et « Contremaître » ; le classeur RH
-- compte pourtant des recyclages STEP. La contrainte de la fonction accepte
-- désormais « STEP ». L'application ne la propose qu'à qui a la STEP en
-- polyvalence validée.

alter table biowanze.recyclages_fiches drop constraint recyclages_fiches_fonction_check;
alter table biowanze.recyclages_fiches add constraint recyclages_fiches_fonction_check
  check (fonction in ('Meunerie','Gluten','Fermentation','Distillation','Chaudières','STEP','Contremaître'));
