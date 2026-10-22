-- DEUX TYPES DE CONGÉ LE MÊME JOUR, ET L'HEURE OÙ L'ON QUITTE OU ARRIVE
-- (le client, le 22/10/2026 : « il faut pouvoir mettre deux sortes de congé,
-- et si on quitte ou arrive plus tôt, le préciser »).
--
-- Une ligne de la courte durée porte, en plus de « code » :
--   « code2 »  un second type demandable, différent du premier ;
--   « part »   'quitte' ou 'arrive', avec « heure » (HH:MM).
-- Acceptée, la journée garde le premier code en annotation (celui que le
-- classeur et les compteurs lisent) ; le second et l'heure s'écrivent dans
-- le commentaire, comme le classeur les note à la main. Le format d'une
-- annotation à deux codes n'est pas connu : on ne l'invente pas.
--
-- Repris de 18-contremaitre-du-jour.sql (demande) et 12-formulaires.sql
-- (décision), seules les lignes marquées changent.

create or replace function public.biowanze_demander_formulaire(p_formulaire text, p_lignes jsonb, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare pid uuid := biowanze.ma_personne(); moi text := biowanze.ma_trigramme();
        l jsonb; j date; propres jsonb := '[]'; vus date[] := '{}'; n int := 0; npause int := 0; nday int := 0;
        prevue text; rp text; rpid uuid; dmin date; dmax date; nid bigint; code1 text; cm0 text; c2 text; part text; hh text;
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
    prevue := biowanze.pause_du_jour(pid, j);
    cm0 := upper(nullif(trim(coalesce(l->>'cm','')),''));
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
      -- un second type de congé le même jour, et l'heure où l'on quitte ou arrive
      c2 := nullif(trim(coalesce(l->>'code2','')),'');
      part := nullif(trim(coalesce(l->>'part','')),'');
      hh := nullif(trim(coalesce(l->>'heure','')),'');
      if c2 is not null then
        if p_formulaire <> 'courte' then raise exception 'un second type de congé se demande sur le formulaire de courte durée'; end if;
        if not biowanze.code_demandable(c2) then raise exception 'second type de congé non demandable : %', c2; end if;
        if c2 = l->>'code' then raise exception 'le % : deux fois le même type de congé', to_char(j,'DD/MM'); end if;
      end if;
      if part is not null or hh is not null then
        if p_formulaire <> 'courte' then raise exception 'une heure de départ ou d''arrivée se précise sur le formulaire de courte durée'; end if;
        if part not in ('quitte','arrive') or hh !~ '^([01]?[0-9]|2[0-3]):[0-5][0-9]$' then raise exception 'le % : heure de départ ou d''arrivée incomplète', to_char(j,'DD/MM'); end if;
      end if;
      l := jsonb_build_object('j', j, 'code', l->>'code', 'rp', l->'rp')
           || case when c2 is not null then jsonb_build_object('code2', c2) else '{}'::jsonb end
           || case when part is not null then jsonb_build_object('part', part, 'heure', hh) else '{}'::jsonb end;
      code1 := coalesce(code1, l->>'code');
    end if;
    rp := upper(nullif(trim(coalesce(l->>'rp','')),''));
    if rp is not null then
      if p_formulaire = 'longue' then raise exception 'le formulaire de longue durée ne porte pas de remplaçant'; end if;
      select id into rpid from biowanze.personnes where trigramme = rp and actif;
      if rpid is null then raise exception 'remplaçant inconnu : %', rp; end if;
      if rp = moi then raise exception 'on ne se remplace pas soi-même'; end if;
      l := l || jsonb_build_object('rp', rp, 'rp_prevue', biowanze.pause_du_jour(rpid, j));
    else
      l := l - 'rp';
    end if;
    l := l || jsonb_build_object('prevue', prevue);
    -- le contremaître de sa pause ce jour-là, lu par l'application dans l'horaire
    if cm0 is not null and cm0 <> moi and exists (select 1 from biowanze.personnes where trigramme = cm0) then
      l := l || jsonb_build_object('cm', cm0);
    end if;
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
      com := 'Demande n° '||d.id
             ||coalesce(' · + '||(l->>'code2'),'')
             ||case when l ? 'part' then ' · '||case when l->>'part' = 'quitte' then 'quitte à ' else 'arrive à ' end||(l->>'heure') else '' end
             ||coalesce(' : '||d.texte,'');
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
