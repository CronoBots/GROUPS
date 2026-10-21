-- LES TROIS FORMULAIRES OFFICIELS DE DEMANDE DE CONGÉ (le client, le
-- 21/10/2026 : « réfère-toi à une demande de congé officielle », puis les
-- trois documents Word du dossier RH « Formulaires de demande de congé –
-- tous départements »). Le module 3 (10-demandes.sql) demandait un code sur
-- une période ; les formulaires demandent UN TABLEAU DE JOURS :
--
--   courte     « Demande de congé de courte durée / remplacement /
--              modification de pause » : 10 lignes au plus ; chaque ligne,
--              le jour, la date, la pause prévue, le type de congé OU la
--              modification de pause, et le remplaçant avec SA pause prévue.
--              Signatures du demandeur et du remplaçant ; visa du
--              responsable : approbation ou refus, motivation, cases
--              « RAPPELABLE » et « À LA DEMANDE DE LA LIGNE HIÉRARCHIQUE ».
--   longue     « Demande de congé de longue durée (≥ 1 semaine) » : 14 jours
--              de pause et 8 jours de DAY ; « max. 2 périodes distinctes » ;
--              à remettre avant le 31 janvier pour le 15 juin – 15 septembre,
--              au plus tard le 31 août pour les deux semaines de fin
--              d'année. Signature du demandeur seule.
--   sans_solde « Demande de congé sans solde » : demandeur, remplaçant ;
--              « ne peuvent être demandés que si le solde des heures de
--              congé / de récupération (y compris ceux déjà planifiés) est à
--              0 » ; « un maximum de 10 jours par an ». Visa : approbation,
--              RESTRICTION, motivation, « RAPPELABLE », refus et motivation.
--
-- La base ne refuse que ce que le formulaire interdit sans appel (plus de
-- lignes que de cases, plus de 10 jours sans solde dans l'année) ; le délai
-- de remise, les deux périodes et le solde à zéro sont MONTRÉS au valideur,
-- qui tranche, comme sur le papier.
--
-- Ligne (jsonb) : {"j":"AAAA-MM-JJ", "code":"VA"} pour un congé,
-- {"j":…, "pause":"AM"} pour une modification de pause, et "rp":"TRI" pour
-- le remplaçant. La base y ajoute "prevue" (la cellule du jour) et
-- "rp_prevue" (celle du remplaçant), lues dans biowanze.journees.

alter table biowanze.demandes add column if not exists formulaire text
  check (formulaire in ('courte','longue','sans_solde'));
alter table biowanze.demandes add column if not exists lignes jsonb not null default '[]';
alter table biowanze.demandes add column if not exists rappelable boolean;
alter table biowanze.demandes add column if not exists a_la_demande boolean;
alter table biowanze.demandes add column if not exists restriction text;
alter table biowanze.demandes add column if not exists motivation text;
alter table biowanze.demandes add column if not exists accords jsonb not null default '{}';

create or replace function biowanze.ma_trigramme()
returns text language sql stable security definer set search_path = '' as $$
  select p.trigramme from biowanze.personnes p where p.id = biowanze.ma_personne()
$$;
revoke all on function biowanze.ma_trigramme() from public, anon, authenticated;

-- Les jours de congé sans solde d'une personne dans l'année (en attente ou
-- acceptés), lignes et anciennes demandes comprises.
create or replace function biowanze.jours_sans_solde(p_pid uuid, p_annee int)
returns int language sql stable security definer set search_path = '' as $$
  select coalesce(sum(case when jsonb_array_length(d.lignes) > 0
           then (select count(*) from jsonb_array_elements(d.lignes) l where l->>'code' = 'CSS')
           else (d.au - d.du + 1) end), 0)::int
  from biowanze.demandes d
  where d.personne_id = p_pid and d.statut in ('en_attente','acceptee')
    and extract(year from d.du) = p_annee
    and (d.formulaire = 'sans_solde' or d.code = 'CSS')
$$;
revoke all on function biowanze.jours_sans_solde(uuid,int) from public, anon, authenticated;

-- Demander, sur l'un des trois formulaires.
create or replace function public.biowanze_demander_formulaire(p_formulaire text, p_lignes jsonb, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare pid uuid := biowanze.ma_personne(); moi text := biowanze.ma_trigramme();
        l jsonb; j date; propres jsonb := '[]'; vus date[] := '{}'; n int := 0; npause int := 0; nday int := 0;
        prevue text; rp text; rpid uuid; dmin date; dmax date; nid bigint; code1 text;
begin
  if pid is null then raise exception 'compte non validé'; end if;
  if p_formulaire not in ('courte','longue','sans_solde') then raise exception 'formulaire inconnu'; end if;
  if jsonb_typeof(p_lignes) <> 'array' or jsonb_array_length(p_lignes) = 0 then raise exception 'aucun jour demandé'; end if;
  for l in select * from jsonb_array_elements(p_lignes) loop
    j := (l->>'j')::date;
    if j is null then raise exception 'date manquante'; end if;
    if j = any(vus) then raise exception 'le % est demandé deux fois', to_char(j,'DD/MM'); end if;
    vus := vus || j;
    if j < current_date - 31 then raise exception 'date trop ancienne : %', to_char(j,'DD/MM/YYYY'); end if;
    select cellule into prevue from biowanze.journees where personne_id = pid and jour = j;
    if p_formulaire = 'sans_solde' then l := jsonb_build_object('j', j, 'code', 'CSS', 'rp', l->'rp'); end if;
    if l ? 'pause' and l->>'pause' is not null then
      if p_formulaire <> 'courte' then raise exception 'la modification de pause se demande sur le formulaire de courte durée'; end if;
      if l->>'pause' not in (select c.code from biowanze.codes c where c.famille = 'poste' and c.code not in ('-','H. flott.')) then
        raise exception 'pause inconnue : %', l->>'pause'; end if;
      if coalesce(prevue,'-') = '-' then raise exception 'le % est un repos : rien à modifier', to_char(j,'DD/MM'); end if;
      if l->>'pause' = prevue then raise exception 'le % : la pause demandée est déjà la pause prévue', to_char(j,'DD/MM'); end if;
      l := jsonb_build_object('j', j, 'pause', l->>'pause', 'rp', l->'rp');
    else
      if not biowanze.code_demandable(l->>'code') then raise exception 'type de congé non demandable : %', coalesce(l->>'code','(vide)'); end if;
      l := jsonb_build_object('j', j, 'code', l->>'code', 'rp', l->'rp');
      code1 := coalesce(code1, l->>'code');
    end if;
    rp := upper(nullif(trim(coalesce(l->>'rp','')),''));
    if rp is not null then
      if p_formulaire = 'longue' then raise exception 'le formulaire de longue durée ne porte pas de remplaçant'; end if;
      select id into rpid from biowanze.personnes where trigramme = rp and actif;
      if rpid is null then raise exception 'remplaçant inconnu : %', rp; end if;
      if rp = moi then raise exception 'on ne se remplace pas soi-même'; end if;
      l := l || jsonb_build_object('rp', rp, 'rp_prevue', (select cellule from biowanze.journees where personne_id = rpid and jour = j));
    else
      l := l - 'rp';
    end if;
    l := l || jsonb_build_object('prevue', prevue);
    if prevue = 'D' then nday := nday + 1; else npause := npause + 1; end if;
    propres := propres || l; n := n + 1;
  end loop;
  if p_formulaire = 'courte' and n > 10 then raise exception 'dix jours au plus sur ce formulaire ; au-delà, le formulaire de longue durée'; end if;
  if p_formulaire = 'longue' and (npause > 14 or nday > 8) then
    raise exception 'quatorze jours de pause et huit jours de DAY au plus'; end if;
  if p_formulaire = 'sans_solde' and n > 10 then raise exception 'dix jours de congé sans solde au plus'; end if;
  select min(x), max(x) into dmin, dmax from unnest(vus) x;
  if extract(year from dmin) <> extract(year from dmax) then raise exception 'une demande par année'; end if;
  if p_formulaire = 'sans_solde' and biowanze.jours_sans_solde(pid, extract(year from dmin)::int) + n > 10 then
    raise exception 'dix jours de congé sans solde par an au plus (déjà % cette année)', biowanze.jours_sans_solde(pid, extract(year from dmin)::int);
  end if;
  if exists (select 1 from biowanze.demandes d where d.personne_id = pid and d.statut = 'en_attente'
             and d.du <= dmax and d.au >= dmin
             and (jsonb_array_length(d.lignes) = 0
                  or exists (select 1 from jsonb_array_elements(d.lignes) x where (x->>'j')::date = any(vus)))) then
    raise exception 'une demande en attente couvre déjà l''un de ces jours';
  end if;
  insert into biowanze.demandes(personne_id, type, du, au, code, texte, cree_par, formulaire, lignes)
    values (pid, 'conge', dmin, dmax, coalesce(code1, 'pause'), nullif(trim(p_texte),''), auth.uid(), p_formulaire,
            (select jsonb_agg(x order by (x->>'j')) from jsonb_array_elements(propres) x))
    returning id into nid;
  return nid;
end $$;

-- La signature du remplaçant : son accord, depuis son propre compte.
create or replace function public.biowanze_accord_remplacant(p_id bigint)
returns text language plpgsql security definer set search_path = '' as $$
declare moi text := biowanze.ma_trigramme();
begin
  if moi is null then raise exception 'compte non validé'; end if;
  update biowanze.demandes set accords = accords || jsonb_build_object(moi, now())
   where id = p_id and statut = 'en_attente'
     and exists (select 1 from jsonb_array_elements(lignes) x where x->>'rp' = moi);
  if not found then raise exception 'demande introuvable, déjà traitée, ou vous n''y êtes pas remplaçant'; end if;
  return 'accord';
end $$;

-- La liste, avec les rubriques des formulaires. Le remplaçant voit les
-- demandes où il est nommé.
create or replace function public.biowanze_liste_demandes()
returns table (id bigint, trigramme text, nom text, prenom text, categorie text, code text, du date, au date, texte text,
               statut text, cm text, cm_le timestamptz, rh text, rh_le timestamptz, motif_refus text, cree_le timestamptz,
               attend_cm boolean, attend_rh boolean, a_moi boolean,
               formulaire text, lignes jsonb, rappelable boolean, a_la_demande boolean, restriction text,
               motivation text, accords jsonb, je_remplace boolean, sans_solde_annee int)
language sql stable security definer set search_path = '' as $$
  select d.id, p.trigramme, p.nom, p.prenom, p.categorie, d.code, d.du, d.au, d.texte, d.statut,
         pc.trigramme, d.valide_cm_le, pr.trigramme, d.valide_rh_le, d.motif_refus, d.cree_le,
         (d.statut = 'en_attente' and d.valide_cm is null and coalesce(cd.role,'operateur') = 'operateur'),
         (d.statut = 'en_attente' and d.valide_rh is null),
         d.personne_id = biowanze.ma_personne(),
         d.formulaire, d.lignes, d.rappelable, d.a_la_demande, d.restriction, d.motivation, d.accords,
         exists (select 1 from jsonb_array_elements(d.lignes) x where x->>'rp' = biowanze.ma_trigramme()),
         case when d.formulaire = 'sans_solde' then biowanze.jours_sans_solde(d.personne_id, extract(year from d.du)::int) end
  from biowanze.demandes d
  join biowanze.personnes p on p.id = d.personne_id
  left join biowanze.comptes cd on cd.user_id = d.cree_par
  left join biowanze.comptes ccm on ccm.user_id = d.valide_cm left join biowanze.personnes pc on pc.id = ccm.personne_id
  left join biowanze.comptes crh on crh.user_id = d.valide_rh left join biowanze.personnes pr on pr.id = crh.personne_id
  where biowanze.role_courant() is not null
    and (biowanze.role_courant() in ('rh','hierarchie') or d.personne_id = biowanze.ma_personne()
         or exists (select 1 from jsonb_array_elements(d.lignes) x where x->>'rp' = biowanze.ma_trigramme()))
  order by (d.statut = 'en_attente') desc, d.du, d.id
$$;

-- Le visa : les cases du formulaire, puis la décision (10-demandes.sql).
create or replace function public.biowanze_viser_demande(p_id bigint, p_accepte boolean, p_motivation text,
                                                         p_rappelable boolean, p_a_la_demande boolean, p_restriction text)
returns text language plpgsql security definer set search_path = '' as $$
begin
  if biowanze.role_courant() not in ('rh','hierarchie') then raise exception 'réservé aux contremaîtres et à la RH'; end if;
  update biowanze.demandes set
      rappelable = coalesce(p_rappelable, rappelable),
      a_la_demande = coalesce(p_a_la_demande, a_la_demande),
      restriction = coalesce(nullif(trim(p_restriction),''), restriction),
      motivation = case when p_accepte then coalesce(nullif(trim(p_motivation),''), motivation) else motivation end
   where id = p_id and statut = 'en_attente';
  return public.biowanze_decider_demande(p_id, p_accepte, case when p_accepte then null else p_motivation end);
end $$;

-- La décision : une demande à LIGNES se pose ligne par ligne. Un congé
-- met son code en annotation (le poste prévu reste, un repos est sauté) ;
-- une modification de pause change la cellule et l'écrit comme le
-- classeur, « changement PM -> AM ». Le jour du remplaçant n'est PAS
-- écrit : quelle cellule et quelle prime lui donner est une question au
-- client (docs/questions-client.md) ; il se pose au planning, comme
-- aujourd'hui dans le classeur.
create or replace function public.biowanze_decider_demande(p_id bigint, p_accepte boolean, p_motif text default null)
returns text language plpgsql security definer set search_path = '' as $$
declare moi biowanze.role := biowanze.role_courant(); d record; role_dem biowanze.role; j date; jr record; nb int := 0;
        l jsonb; cel text; ann text; com text;
begin
  if moi not in ('rh','hierarchie') then raise exception 'réservé aux contremaîtres et à la RH'; end if;
  select * into d from biowanze.demandes where id = p_id for update;
  if not found or d.statut <> 'en_attente' then raise exception 'demande introuvable ou déjà traitée'; end if;
  if d.personne_id = biowanze.ma_personne() then raise exception 'on ne valide pas sa propre demande'; end if;
  select coalesce(c.role,'operateur') into role_dem from biowanze.comptes c where c.user_id = d.cree_par;
  if not p_accepte then
    update biowanze.demandes set statut = 'refusee', motif_refus = nullif(trim(p_motif),''),
      valide_cm = case when moi = 'hierarchie' then auth.uid() else valide_cm end,
      valide_cm_le = case when moi = 'hierarchie' then now() else valide_cm_le end,
      valide_rh = case when moi = 'rh' then auth.uid() else valide_rh end,
      valide_rh_le = case when moi = 'rh' then now() else valide_rh_le end
     where id = p_id;
    return 'refusee';
  end if;
  if moi = 'hierarchie' then
    if coalesce(role_dem,'operateur') <> 'operateur' then raise exception 'la demande d''un cadre ne se valide que par la RH'; end if;
    update biowanze.demandes set valide_cm = auth.uid(), valide_cm_le = now() where id = p_id;
  else
    update biowanze.demandes set valide_rh = auth.uid(), valide_rh_le = now() where id = p_id;
  end if;
  select * into d from biowanze.demandes where id = p_id;
  if d.valide_rh is null or (coalesce(role_dem,'operateur') = 'operateur' and d.valide_cm is null) then
    return 'validee_en_partie';
  end if;
  -- acceptée : chaque jour se pose, comme une saisie
  for l in select * from jsonb_array_elements(case when jsonb_array_length(d.lignes) > 0 then d.lignes
           else (select jsonb_agg(jsonb_build_object('j', g::date, 'code', d.code)) from generate_series(d.du, d.au, interval '1 day') g) end) loop
    j := (l->>'j')::date;
    select cellule, annotation, commentaire into jr from biowanze.journees where personne_id = d.personne_id and jour = j;
    if jr.cellule is null or jr.cellule = '-' then continue; end if;
    if l ? 'pause' then
      cel := l->>'pause'; ann := jr.annotation;
      com := 'changement '||jr.cellule||' -> '||cel||' (demande n° '||d.id||')';
    else
      cel := jr.cellule; ann := l->>'code';
      com := 'Demande n° '||d.id||coalesce(' : '||d.texte,'');
    end if;
    insert into biowanze.journees(personne_id, jour, cellule, annotation, commentaire, source, maj_par, maj_le)
      values (d.personne_id, j, cel, ann, com, 'saisie', auth.uid(), now())
    on conflict (personne_id, jour) do update set
      cl_cellule = case when biowanze.journees.source = 'classeur' then biowanze.journees.cellule else biowanze.journees.cl_cellule end,
      cl_annotation = case when biowanze.journees.source = 'classeur' then biowanze.journees.annotation else biowanze.journees.cl_annotation end,
      cl_commentaire = case when biowanze.journees.source = 'classeur' then biowanze.journees.commentaire else biowanze.journees.cl_commentaire end,
      cellule = excluded.cellule, annotation = excluded.annotation, commentaire = excluded.commentaire,
      source = 'saisie', maj_par = auth.uid(), maj_le = now();
    nb := nb + 1;
  end loop;
  update biowanze.demandes set statut = 'acceptee' where id = p_id;
  return 'acceptee:'||nb;
end $$;

revoke all on function public.biowanze_demander_formulaire(text,jsonb,text) from public, anon;
revoke all on function public.biowanze_accord_remplacant(bigint) from public, anon;
revoke all on function public.biowanze_liste_demandes() from public, anon;
revoke all on function public.biowanze_viser_demande(bigint,boolean,text,boolean,boolean,text) from public, anon;
grant execute on function public.biowanze_demander_formulaire(text,jsonb,text) to authenticated;
grant execute on function public.biowanze_accord_remplacant(bigint) to authenticated;
grant execute on function public.biowanze_liste_demandes() to authenticated;
grant execute on function public.biowanze_viser_demande(bigint,boolean,text,boolean,boolean,text) to authenticated;
