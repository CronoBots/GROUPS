-- LE CONTREMAÎTRE DU JOUR, APRÈS LE REMPLAÇANT (le client, le 22/10/2026) :
-- « c'est le contremaître qui a la fonction ce jour-là qui doit être
-- notifié de la demande faite durant sa pause ; sinon cela doit bien
-- apparaître pour tous les autres contremaîtres et adjoints », et « non,
-- toujours le remplaçant avant le contremaître ».
--
--  1. Chaque ligne d'une demande porte « cm » : le contremaître de la pause
--     du demandeur ce jour-là, lu par l'application dans l'horaire (la
--     ligne « Contremaître » du Planning ; la base ne connaît pas les
--     postes). Pas lui-même, et un trigramme connu.
--  2. Quand la demande est complète (aucun remplaçant, ou la dernière
--     signature), il est notifié, en même temps que la RH. Les autres
--     comptes hiérarchie (contremaîtres et adjoints) la voient dans leur
--     liste, comme avant.
--  3. « attend_cm » n'est vrai qu'une fois les remplaçants signés, et la
--     base refuse le visa du contremaître avant (la garde de la RH, 14,
--     s'étend à la hiérarchie).

create or replace function public.biowanze_demander_formulaire(p_formulaire text, p_lignes jsonb, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare pid uuid := biowanze.ma_personne(); moi text := biowanze.ma_trigramme();
        l jsonb; j date; propres jsonb := '[]'; vus date[] := '{}'; n int := 0; npause int := 0; nday int := 0;
        prevue text; rp text; rpid uuid; dmin date; dmax date; nid bigint; code1 text; cm0 text;
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
      l := jsonb_build_object('j', j, 'code', l->>'code', 'rp', l->'rp');
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

create or replace function biowanze.demandes_notifier()
returns trigger language plpgsql security definer set search_path = '' as $$
declare dem text; per text; n int := 0; rp text;
begin
  if new.statut <> 'en_attente' then return new; end if;
  select trigramme into dem from biowanze.personnes where id = new.personne_id;
  per := case when new.du = new.au then 'le '||to_char(new.du,'DD/MM')
              else 'du '||to_char(new.du,'DD/MM')||' au '||to_char(new.au,'DD/MM') end;
  if tg_op = 'INSERT' then
    for rp in select distinct x->>'rp' from jsonb_array_elements(new.lignes) x where coalesce(x->>'rp','') <> '' loop
      insert into biowanze.notifs(tri, titre, texte, demande_id)
        values (rp, 'Remplacement à signer', coalesce(dem,'Un collègue')||' vous demande de le remplacer '||per||'. Touchez pour lire et signer.', new.id);
      n := n + 1;
    end loop;
  end if;
  if biowanze.accords_complets(new.lignes, new.accords)
     and (tg_op = 'INSERT' or not biowanze.accords_complets(old.lignes, old.accords)) then
    insert into biowanze.notifs(tri, titre, texte, demande_id)
      select distinct p.trigramme, 'Demande de congé à viser',
             coalesce(dem,'?')||' : demande '||per||case when tg_op = 'UPDATE' then ', remplacement signé.' else '.' end, new.id
        from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id
       where c.role = 'rh' and c.valide and p.trigramme is not null;
    n := n + 1;
    -- le contremaître qui a la fonction ce jour-là, à la pause du demandeur
    insert into biowanze.notifs(tri, titre, texte, demande_id)
      select distinct x->>'cm', 'Demande de congé à viser',
             coalesce(dem,'?')||' : demande '||per||' pendant votre pause'||case when tg_op = 'UPDATE' then ', remplacement signé.' else '.' end, new.id
        from jsonb_array_elements(new.lignes) x
       where coalesce(x->>'cm','') <> '' and x->>'cm' is distinct from dem;
    if tg_op = 'UPDATE' and dem is not null then
      insert into biowanze.notifs(tri, titre, texte, demande_id)
        values (dem, 'Remplacement signé', 'Votre remplaçant a signé votre demande '||per||' : elle part chez le contremaître et la RH.', new.id);
    end if;
  end if;
  if n > 0 then perform biowanze.lancer_notifs(); end if;
  return new;
end $$;

create or replace function biowanze.demandes_garde_rh()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if biowanze.role_courant() in ('rh','hierarchie') and old.statut = 'en_attente'
     and ((new.valide_rh is not null and old.valide_rh is null) or (new.valide_cm is not null and old.valide_cm is null)
          or new.statut in ('acceptee','refusee'))
     and not biowanze.accords_complets(new.lignes, new.accords) then
    raise exception 'le remplaçant n''a pas encore signé : la demande arrive chez le contremaître et la RH après sa signature';
  end if;
  return new;
end $$;

-- la liste (16-effacer.sql, une ligne changée)
create or replace function public.biowanze_liste_demandes()
returns table (id bigint, trigramme text, nom text, prenom text, categorie text, code text, du date, au date, texte text,
               statut text, cm text, cm_le timestamptz, rh text, rh_le timestamptz, motif_refus text, cree_le timestamptz,
               attend_cm boolean, attend_rh boolean, a_moi boolean,
               formulaire text, lignes jsonb, rappelable boolean, a_la_demande boolean, restriction text,
               motivation text, accords jsonb, je_remplace boolean, sans_solde_annee int)
language sql stable security definer set search_path = '' as $$
  select d.id, p.trigramme, p.nom, p.prenom, p.categorie, d.code, d.du, d.au, d.texte, d.statut,
         pc.trigramme, d.valide_cm_le, pr.trigramme, d.valide_rh_le, d.motif_refus, d.cree_le,
         (d.statut = 'en_attente' and d.valide_cm is null and coalesce(cd.role,'operateur') = 'operateur' and biowanze.accords_complets(d.lignes, d.accords)),
         (d.statut = 'en_attente' and d.valide_rh is null and biowanze.accords_complets(d.lignes, d.accords)),
         d.personne_id = biowanze.ma_personne(),
         d.formulaire, d.lignes, d.rappelable, d.a_la_demande, d.restriction, d.motivation, d.accords,
         exists (select 1 from jsonb_array_elements(d.lignes) x where x->>'rp' = biowanze.ma_trigramme()),
         case when d.formulaire = 'sans_solde' then biowanze.jours_sans_solde(d.personne_id, extract(year from d.du)::int) end
  from biowanze.demandes d
  join biowanze.personnes p on p.id = d.personne_id
  left join biowanze.comptes cd on cd.user_id = d.cree_par
  left join biowanze.comptes ccm on ccm.user_id = d.valide_cm left join biowanze.personnes pc on pc.id = ccm.personne_id
  left join biowanze.comptes crh on crh.user_id = d.valide_rh left join biowanze.personnes pr on pr.id = crh.personne_id
  where biowanze.role_courant() is not null and d.statut <> 'annulee'
    and (biowanze.role_courant() in ('rh','hierarchie') or d.personne_id = biowanze.ma_personne()
         or exists (select 1 from jsonb_array_elements(d.lignes) x where x->>'rp' = biowanze.ma_trigramme()))
  order by (d.statut = 'en_attente') desc, d.du, d.id
$$;
