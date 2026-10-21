-- MODULE 1 DE LA PLATEFORME : la saisie des journées par la RH et la ligne
-- hiérarchique (le client, le 20/10/2026 : « le RH et la ligne
-- hiérarchique » saisissent ; le 21/10 : « GO »). docs/plateforme.md.
--
-- La LISTE FERMÉE des codes : les 14 classeurs de fonction n'ont aucune
-- liste déroulante, d'où 186 annotations différentes et 44 compteurs que
-- leurs formules ne comptent pas. Les écritures sont celles que le classeur
-- emploie le plus (l'application les lit déjà), les heures celles des
-- formules du pied (un VA vaut 8 h, un demi 4 h). Plus « xxx », jamais
-- employé.
create table if not exists biowanze.codes (
  code text primary key,
  famille text not null,          -- poste, conge, flex, recup, absence, remplacement, formation, syndical, arret, atelier
  libelle text not null,
  heures numeric(4,2),            -- ce que vaut le code dans les compteurs du pied
  unite text,                     -- h (heures), j (jours)
  ordre int not null default 0,
  actif boolean not null default true
);
alter table biowanze.codes enable row level security;

insert into biowanze.codes(code, famille, libelle, heures, unite, ordre) values
  ('AM','poste','Matin, 6 h – 14 h',null,null,1),
  ('PM','poste','Après-midi, 14 h – 22 h',null,null,2),
  ('N','poste','Nuit, 22 h – 6 h',null,null,3),
  ('D','poste','Jour',null,null,4),
  ('-','poste','Repos (ou poste non presté)',null,null,5),
  ('H. flott.','poste','Horaire flottant',null,null,6),
  ('VA','conge','Vacances annuelles',8,'h',10),
  ('1/2VA','conge','Demi-jour de vacances',4,'h',11),
  ('RTT','conge','Récup. temps de travail',8,'h',12),
  ('1h RTT','conge','1 h de RTT',1,'h',13),('2h RTT','conge','2 h de RTT',2,'h',14),
  ('3h RTT','conge','3 h de RTT',3,'h',15),('4h RTT','conge','4 h de RTT',4,'h',16),
  ('5h RTT','conge','5 h de RTT',5,'h',17),('6h RTT','conge','6 h de RTT',6,'h',18),
  ('7h RTT','conge','7 h de RTT',7,'h',19),
  ('DTT','conge','Congé d''ancienneté',8,'h',20),
  ('1/2DTT','conge','Demi-jour d''ancienneté',4,'h',21),
  ('RJF','conge','Récup. jour férié',8,'h',22),
  ('1/2RJF','conge','Demi-jour férié récupéré',4,'h',23),
  ('CP','conge','Congé parental',1,'j',24),
  ('TP','conge','Temps partiel',1,'j',25),
  ('CT','conge','Crédit-temps',1,'j',26),
  ('CEP','conge','Congé éducation payé',null,null,27),
  ('CSS','conge','Congé sans solde',null,null,28),
  ('1h +FT','flex','Flex time, 1 h de plus',1,'h',30),('2h +FT','flex','Flex time, 2 h de plus',2,'h',31),
  ('3h +FT','flex','Flex time, 3 h de plus',3,'h',32),('4h +FT','flex','Flex time, 4 h de plus',4,'h',33),
  ('5h +FT','flex','Flex time, 5 h de plus',5,'h',34),('6h +FT','flex','Flex time, 6 h de plus',6,'h',35),
  ('7h +FT','flex','Flex time, 7 h de plus',7,'h',36),('8h +FT','flex','Flex time, 8 h de plus',8,'h',37),
  ('1h -FT','flex','Flex time, 1 h de moins',-1,'h',40),('2h -FT','flex','Flex time, 2 h de moins',-2,'h',41),
  ('3h -FT','flex','Flex time, 3 h de moins',-3,'h',42),('4h -FT','flex','Flex time, 4 h de moins',-4,'h',43),
  ('5h -FT','flex','Flex time, 5 h de moins',-5,'h',44),('6h -FT','flex','Flex time, 6 h de moins',-6,'h',45),
  ('7h -FT','flex','Flex time, 7 h de moins',-7,'h',46),('8h -FT','flex','Flex time, 8 h de moins',-8,'h',47),
  ('RHS','recup','Récup. d''heures supplémentaires, journée',8,'h',50),
  ('1h rhs','recup','1 h récupérée',1,'h',51),('2h rhs','recup','2 h récupérées',2,'h',52),
  ('3h rhs','recup','3 h récupérées',3,'h',53),('4h rhs','recup','4 h récupérées',4,'h',54),
  ('Abs','absence','Absence – maladie',null,null,60),
  ('R','remplacement','Remplacement',null,null,70),
  ('R-CM','remplacement','Remplacement contremaître',null,null,71),
  ('F','formation','Formation',null,null,80),
  ('D-F','formation','Formation, horaire de jour',null,null,81),
  ('VM','formation','Visite médicale',null,null,82),
  ('DS','syndical','Délégation syndicale',null,null,90),
  ('DS-CE','syndical','Délégation syndicale, conseil d''entreprise',null,null,91),
  ('CPPT','syndical','CPPT',null,null,92),
  ('D-CPPT','syndical','CPPT, horaire de jour',null,null,93),
  ('SD26','arret','Arrêt SD26',null,null,100),
  ('E. min SD26','arret','Arrêt SD26, effectif minimum',null,null,101),
  ('meunerie','atelier','Atelier : meunerie',null,null,110),
  ('gluten','atelier','Atelier : gluten',null,null,111),
  ('Ferm. Liq.','atelier','Atelier : fermentation',null,null,112),
  ('distillation','atelier','Atelier : distillation',null,null,113),
  ('poly. Arr.','atelier','Atelier : polyvalent arrière',null,null,114),
  ('terr. Arr.','atelier','Atelier : terrain arrière',null,null,115),
  ('Poly. Etoh','atelier','Atelier : éthanol',null,null,116),
  ('chaudières','atelier','Atelier : chaudières',null,null,117),
  ('STEP','atelier','Atelier : station d''épuration',null,null,118)
on conflict (code) do nothing;

-- Une plage horaire s'écrit « 6h-18h », « 18h-06h », « 8h30-16h30 ».
create or replace function biowanze.code_valide(p text)
returns boolean language sql stable security definer set search_path = '' as $$
  select p is null
      or exists (select 1 from biowanze.codes c where c.code = p and c.actif)
      or p ~ '^\d{1,2}h(\d{2})?-\d{1,2}h(\d{2})?$'
$$;

-- Pendant l'étape 2 le classeur continue d'arriver : une journée SAISIE
-- garde ce que le classeur en dit à côté (cl_*), pour voir où les deux
-- divergent, et la saisie ne l'écrase jamais.
alter table biowanze.journees add column if not exists cl_cellule text;
alter table biowanze.journees add column if not exists cl_annotation text;
alter table biowanze.journees add column if not exists cl_commentaire text;

-- La liste des codes, pour tout compte validé.
create or replace function public.biowanze_codes()
returns table (code text, famille text, libelle text, heures numeric, unite text, ordre int)
language sql stable security definer set search_path = '' as $$
  select c.code, c.famille, c.libelle, c.heures, c.unite, c.ordre
  from biowanze.codes c where c.actif and biowanze.role_courant() is not null
  order by c.ordre
$$;

-- Saisir une journée : la RH et la hiérarchie. Le prévu et l'annotation
-- doivent être dans la liste fermée (ou une plage horaire) ; le commentaire
-- reste libre, en attendant les événements structurés (module 2).
create or replace function public.biowanze_saisir(p_trigramme text, p_jour date,
  p_cellule text, p_annotation text, p_commentaire text)
returns text language plpgsql security definer set search_path = '' as $$
declare pid uuid; c text := nullif(trim(p_cellule),''); a text := nullif(trim(p_annotation),'');
        m text := nullif(trim(p_commentaire),'');
begin
  if biowanze.role_courant() not in ('rh','hierarchie') then raise exception 'réservé à la RH et à la hiérarchie'; end if;
  if not biowanze.code_valide(c) then raise exception 'poste prévu inconnu : %', c; end if;
  if not biowanze.code_valide(a) then raise exception 'code inconnu : %', a; end if;
  if extract(year from p_jour) not between 2026 and 2100 then raise exception 'date hors des années tenues'; end if;
  select id into pid from biowanze.personnes where trigramme = p_trigramme;
  if pid is null then raise exception 'personne inconnue'; end if;
  insert into biowanze.journees(personne_id, jour, cellule, annotation, commentaire, source, maj_par, maj_le)
    values (pid, p_jour, c, a, m, 'saisie', auth.uid(), now())
  on conflict (personne_id, jour) do update set
    -- la première saisie garde ce que le classeur disait
    cl_cellule = case when biowanze.journees.source = 'classeur' then biowanze.journees.cellule else biowanze.journees.cl_cellule end,
    cl_annotation = case when biowanze.journees.source = 'classeur' then biowanze.journees.annotation else biowanze.journees.cl_annotation end,
    cl_commentaire = case when biowanze.journees.source = 'classeur' then biowanze.journees.commentaire else biowanze.journees.cl_commentaire end,
    cellule = excluded.cellule, annotation = excluded.annotation, commentaire = excluded.commentaire,
    source = 'saisie', maj_par = auth.uid(), maj_le = now();
  return 'saisie';
end $$;

-- Annuler une saisie : la journée redevient celle du classeur.
create or replace function public.biowanze_annuler_saisie(p_trigramme text, p_jour date)
returns text language plpgsql security definer set search_path = '' as $$
begin
  if biowanze.role_courant() not in ('rh','hierarchie') then raise exception 'réservé à la RH et à la hiérarchie'; end if;
  update biowanze.journees j
     set cellule = j.cl_cellule, annotation = j.cl_annotation, commentaire = j.cl_commentaire,
         cl_cellule = null, cl_annotation = null, cl_commentaire = null,
         source = 'classeur', maj_par = auth.uid(), maj_le = now()
    from biowanze.personnes p
   where p.id = j.personne_id and p.trigramme = p_trigramme and j.jour = p_jour and j.source = 'saisie';
  if not found then raise exception 'aucune saisie ce jour-là'; end if;
  return 'annulee';
end $$;

-- Les saisies d'une année, pour tout compte validé : l'application les pose
-- par-dessus l'horaire du classeur. Avec l'auteur et ce que dit le classeur.
create or replace function public.biowanze_saisies(p_annee int)
returns table (trigramme text, jour date, cellule text, annotation text, commentaire text,
               cl_cellule text, cl_annotation text, cl_commentaire text, maj_le timestamptz, auteur text)
language sql stable security definer set search_path = '' as $$
  select p.trigramme, j.jour, j.cellule, j.annotation, j.commentaire,
         j.cl_cellule, j.cl_annotation, j.cl_commentaire, j.maj_le, pa.trigramme
  from biowanze.journees j
  join biowanze.personnes p on p.id = j.personne_id
  left join biowanze.comptes ca on ca.user_id = j.maj_par
  left join biowanze.personnes pa on pa.id = ca.personne_id
  where j.source = 'saisie' and biowanze.role_courant() is not null
    and j.jour between make_date(p_annee,1,1) and make_date(p_annee,12,31)
  order by p.trigramme, j.jour
$$;

revoke all on function public.biowanze_codes() from public, anon;
revoke all on function public.biowanze_saisir(text,date,text,text,text) from public, anon;
revoke all on function public.biowanze_annuler_saisie(text,date) from public, anon;
revoke all on function public.biowanze_saisies(int) from public, anon;
grant execute on function public.biowanze_codes() to authenticated;
grant execute on function public.biowanze_saisir(text,date,text,text,text) to authenticated;
grant execute on function public.biowanze_annuler_saisie(text,date) to authenticated;
grant execute on function public.biowanze_saisies(int) to authenticated;
revoke all on function biowanze.code_valide(text) from public, anon, authenticated;

-- L'HISTORIQUE DES SAISIES, pour la RH et la hiérarchie (l'espace RH,
-- 21/10/2026) : qui a changé quelle journée, quand, avant et après. Les
-- écritures du robot (sans auteur) n'y sont pas.
create or replace function public.biowanze_historique(p_limite int default 60)
returns table (quand timestamptz, auteur text, trigramme text, jour date, operation text,
               avant_cellule text, avant_annotation text, apres_cellule text, apres_annotation text, apres_source text, commentaire text)
language sql stable security definer set search_path = '' as $$
  select h.quand, pa.trigramme, p.trigramme, coalesce((h.apres->>'jour')::date, (h.avant->>'jour')::date),
         h.operation, h.avant->>'cellule', h.avant->>'annotation', h.apres->>'cellule', h.apres->>'annotation',
         h.apres->>'source', h.apres->>'commentaire'
  from biowanze.historique h
  left join biowanze.personnes p on p.id = coalesce((h.apres->>'personne_id')::uuid, (h.avant->>'personne_id')::uuid)
  left join biowanze.comptes ca on ca.user_id = h.auteur
  left join biowanze.personnes pa on pa.id = ca.personne_id
  where h.table_nom = 'journees' and h.auteur is not null
    and biowanze.role_courant() in ('rh','hierarchie')
  order by h.quand desc
  limit least(greatest(coalesce(p_limite,60),1),500)
$$;
revoke all on function public.biowanze_historique(int) from public, anon;
grant execute on function public.biowanze_historique(int) to authenticated;
