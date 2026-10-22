-- LE CONTREMAÎTRE DE PAUSE VALIDE, PUIS LA RH CONFIRME (le client, le
-- 22/10/2026 : « il manque l'étape de signature du contremaître de pause,
-- c'est lui qui valide la demande, puis la RH confirme et accepte pour que
-- cela soit encodé dans l'horaire »).
--
-- Corrige deux lectures du 20/10 (« les contremaîtres et RH »,
-- base/10-demandes.sql) que le client n'avait pas dites :
--   * « dans n'importe quel ordre » : désormais remplaçant → contremaître
--     → RH. La RH n'accepte qu'après le visa d'un contremaître ; elle peut
--     toujours refuser (un refus suffit, à toute étape) ;
--   * « la demande d'un cadre n'attend que la RH » : TOUTE demande passe
--     par l'étape du contremaître, celle d'un contremaître comme celle
--     d'un compte RH (le client a un compte RH et, contremaître, voulait
--     cette étape sur sa propre demande). Nul ne valide sa propre demande.
-- L'étape du contremaître se signe par un compte hiérarchie, ou par un
-- compte RH (aujourd'hui les seuls comptes validés sont des comptes RH,
-- dont celui du client, contremaître) ; la RH confirme ensuite, et pas
-- avec le compte qui a signé l'étape du contremaître.
-- Les notifications suivent : le contremaître du jour (à défaut, la
-- hiérarchie et la RH, sauf le demandeur) quand les remplaçants ont
-- signé ; la RH quand le contremaître a validé.

-- toute demande passe par le contremaître (gardée en fonction : la règle
-- se lit en un seul endroit, la décision et les notifications la partagent)
create or replace function biowanze.demande_cm_requis(p_cree_par uuid)
returns boolean language sql stable security definer set search_path = '' as $$
  select true
$$;
revoke all on function biowanze.demande_cm_requis(uuid) from public, anon, authenticated;

create or replace function public.biowanze_decider_demande(p_id bigint, p_accepte boolean, p_motif text default null)
returns text language plpgsql security definer set search_path = '' as $$
declare moi biowanze.role := biowanze.role_courant(); d record; cm_requis boolean; j date; jr record; nb int := 0;
        l jsonb; cel text; ann text; com text;
begin
  if moi not in ('rh','hierarchie') then raise exception 'réservé aux contremaîtres et à la RH'; end if;
  select * into d from biowanze.demandes where id = p_id for update;
  if not found or d.statut <> 'en_attente' then raise exception 'demande introuvable ou déjà traitée'; end if;
  if d.personne_id = biowanze.ma_personne() then raise exception 'on ne valide pas sa propre demande'; end if;
  cm_requis := biowanze.demande_cm_requis(d.cree_par);
  if moi = 'hierarchie' and d.valide_cm is not null then
    raise exception 'déjà validée par un contremaître : la RH décide ensuite';
  end if;
  if not p_accepte then
    update biowanze.demandes set statut = 'refusee', motif_refus = nullif(trim(p_motif),''),
      -- le refus se porte à l'étape où il est donné
      valide_cm = case when d.valide_cm is null then auth.uid() else valide_cm end,
      valide_cm_le = case when d.valide_cm is null then now() else valide_cm_le end,
      valide_rh = case when d.valide_cm is not null then auth.uid() else valide_rh end,
      valide_rh_le = case when d.valide_cm is not null then now() else valide_rh_le end
     where id = p_id;
    return 'refusee';
  end if;
  -- d'abord l'étape du contremaître (hiérarchie, ou un compte RH), puis la RH
  if cm_requis and d.valide_cm is null then
    update biowanze.demandes set valide_cm = auth.uid(), valide_cm_le = now() where id = p_id;
  elsif moi = 'hierarchie' then
    raise exception 'déjà validée par un contremaître : la RH confirme ensuite';
  else
    if d.valide_cm = auth.uid() then raise exception 'la RH confirme avec un autre compte que celui qui a validé comme contremaître'; end if;
    update biowanze.demandes set valide_rh = auth.uid(), valide_rh_le = now() where id = p_id;
  end if;
  select * into d from biowanze.demandes where id = p_id;
  if d.valide_rh is null or (cm_requis and d.valide_cm is null) then
    return 'validee_en_partie';
  end if;
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

-- la liste (18, deux lignes changées : attend_cm pour toute demande ;
-- attend_rh une fois le contremaître passé, et pas pour qui l'a signé)
create or replace function public.biowanze_liste_demandes()
returns table (id bigint, trigramme text, nom text, prenom text, categorie text, code text, du date, au date, texte text,
               statut text, cm text, cm_le timestamptz, rh text, rh_le timestamptz, motif_refus text, cree_le timestamptz,
               attend_cm boolean, attend_rh boolean, a_moi boolean,
               formulaire text, lignes jsonb, rappelable boolean, a_la_demande boolean, restriction text,
               motivation text, accords jsonb, je_remplace boolean, sans_solde_annee int)
language sql stable security definer set search_path = '' as $$
  select d.id, p.trigramme, p.nom, p.prenom, p.categorie, d.code, d.du, d.au, d.texte, d.statut,
         pc.trigramme, d.valide_cm_le, pr.trigramme, d.valide_rh_le, d.motif_refus, d.cree_le,
         (d.statut = 'en_attente' and d.valide_cm is null and biowanze.accords_complets(d.lignes, d.accords)),
         (d.statut = 'en_attente' and d.valide_rh is null and d.valide_cm is not null and d.valide_cm is distinct from auth.uid()
            and biowanze.accords_complets(d.lignes, d.accords)),
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

-- les notifications, dans l'ordre du circuit
create or replace function biowanze.demandes_notifier()
returns trigger language plpgsql security definer set search_path = '' as $$
declare dem text; per text; n int := 0; rp text; cm_requis boolean; ncm int;
begin
  if new.statut <> 'en_attente' then return new; end if;
  select trigramme into dem from biowanze.personnes where id = new.personne_id;
  cm_requis := biowanze.demande_cm_requis(new.cree_par);
  per := case when new.du = new.au then 'le '||to_char(new.du,'DD/MM')
              else 'du '||to_char(new.du,'DD/MM')||' au '||to_char(new.au,'DD/MM') end;
  if tg_op = 'INSERT' then
    for rp in select distinct x->>'rp' from jsonb_array_elements(new.lignes) x where coalesce(x->>'rp','') <> '' loop
      insert into biowanze.notifs(tri, titre, texte, demande_id)
        values (rp, 'Remplacement à signer', coalesce(dem,'Un collègue')||' vous demande de le remplacer '||per||'. Touchez pour lire et signer.', new.id);
      n := n + 1;
    end loop;
  end if;
  -- les remplaçants ont tous signé (ou il n'y en a pas) : au contremaître
  if biowanze.accords_complets(new.lignes, new.accords)
     and (tg_op = 'INSERT' or not biowanze.accords_complets(old.lignes, old.accords)) then
    if cm_requis then
      -- le contremaître qui a la fonction ce jour-là, à la pause du demandeur
      insert into biowanze.notifs(tri, titre, texte, demande_id)
        select distinct x->>'cm', 'Demande de congé à valider',
               coalesce(dem,'?')||' : demande '||per||' pendant votre pause'||case when tg_op = 'UPDATE' then ', remplacement signé.' else '.' end, new.id
          from jsonb_array_elements(new.lignes) x
         where coalesce(x->>'cm','') <> '' and x->>'cm' is distinct from dem;
      get diagnostics ncm = row_count;
      -- personne de connu ce jour-là : toute la hiérarchie, sauf le demandeur
      if ncm = 0 then
        insert into biowanze.notifs(tri, titre, texte, demande_id)
          select distinct p.trigramme, 'Demande de congé à valider',
                 coalesce(dem,'?')||' : demande '||per||'.', new.id
            from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id
           where c.role in ('hierarchie','rh') and c.valide and p.trigramme is not null and p.trigramme is distinct from dem;
      end if;
    else
      insert into biowanze.notifs(tri, titre, texte, demande_id)
        select distinct p.trigramme, 'Demande de congé à confirmer', coalesce(dem,'?')||' : demande '||per||'.', new.id
          from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id
         where c.role = 'rh' and c.valide and p.trigramme is not null;
    end if;
    n := n + 1;
    if tg_op = 'UPDATE' and dem is not null then
      insert into biowanze.notifs(tri, titre, texte, demande_id)
        values (dem, 'Remplacement signé', 'Votre remplaçant a signé votre demande '||per||' : elle part chez '||case when cm_requis then 'le contremaître' else 'la RH' end||'.', new.id);
    end if;
  end if;
  -- le contremaître a validé : à la RH, et le demandeur le sait
  if tg_op = 'UPDATE' and new.valide_cm is not null and old.valide_cm is null then
    insert into biowanze.notifs(tri, titre, texte, demande_id)
      select distinct p.trigramme, 'Demande de congé à confirmer',
             coalesce(dem,'?')||' : demande '||per||', validée par le contremaître.', new.id
        from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id
       where c.role = 'rh' and c.valide and p.trigramme is not null and c.user_id is distinct from new.valide_cm;
    if dem is not null then
      insert into biowanze.notifs(tri, titre, texte, demande_id)
        values (dem, 'Demande validée par le contremaître', 'Votre demande '||per||' est validée par le contremaître : elle part à la RH.', new.id);
    end if;
    n := n + 1;
  end if;
  if n > 0 then perform biowanze.lancer_notifs(); end if;
  return new;
end $$;

-- le visa du contremaître réveille aussi le déclencheur (il ne regardait
-- que les signatures des remplaçants)
create or replace trigger demandes_notifier after insert or update of accords, valide_cm on biowanze.demandes
  for each row execute function biowanze.demandes_notifier();
