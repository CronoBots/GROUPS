-- SUPPRIMER, C'EST EFFACER (le client, le 22/10/2026 : « une demande peut
-- être supprimée tant qu'elle n'a été signée par aucune autre personne que
-- soi », puis « les demandes supprimées, donc annulées, peuvent être
-- effacées et n'ont pas besoin d'être visibles »).
--
--  1. Supprimer sa demande l'EFFACE, et la base le refuse dès qu'un autre
--     a signé : remplaçant, contremaître ou RH (jusqu'ici l'écran seul
--     retenait l'accord du remplaçant). Ses notifications pas encore
--     parties s'effacent avec elle : le remplaçant ne reçoit pas une
--     demande qui n'existe plus.
--  2. Modifier sa demande efface l'ancienne au lieu de la garder
--     « annulée » (13-modifier.sql).
--  3. Supprimer sa fiche de recyclage l'efface (15-recyclages.sql).
--  4. Les listes ne montrent plus rien d'annulé.
-- La table biowanze.historique garde, elle, la trace de chaque effacement
-- (déclencheur « tracer », 01-fondations.sql).

-- APPLIQUÉ le 22/10/2026 : la garde, et les listes sans rien d'annulé.
-- La demande supprimée reste « annulee », invisible, en attendant
-- l'effacement ci-dessous.
create or replace function public.biowanze_annuler_demande(p_id bigint)
returns text language plpgsql security definer set search_path = '' as $$
declare d record;
begin
  select * into d from biowanze.demandes where id = p_id and personne_id = biowanze.ma_personne() and statut = 'en_attente' for update;
  if not found then raise exception 'demande introuvable ou déjà traitée'; end if;
  if d.valide_cm is not null or d.valide_rh is not null or coalesce(d.accords,'{}'::jsonb) <> '{}'::jsonb then
    raise exception 'déjà signée par une autre personne : elle ne se supprime plus';
  end if;
  -- ses notifications pas encore parties ne partiront pas
  update biowanze.notifs set envoye_le = now() where demande_id = p_id and envoye_le is null;
  update biowanze.demandes set statut = 'annulee' where id = p_id;
  return 'annulee';
end $$;

-- les listes, sans rien d'annulé (14-remplacant-puis-rh.sql et 15-recyclages.sql, une ligne changée)
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

create or replace function public.biowanze_liste_recyclages()
returns table (id bigint, trigramme text, nom text, prenom text, categorie text, fonction text, jour date, pause text,
               doublure boolean, titulaire text, cm text, texte text, statut text,
               cm_qui text, cm_le timestamptz, cm_motif text, zone_qui text, zone_le timestamptz, rh_qui text, rh_le timestamptz, rh_motif text, cree_le timestamptz,
               a_moi boolean, je_confirme boolean, je_contresigne boolean, je_valide boolean)
language sql stable security definer set search_path = '' as $$
  select f.id, p.trigramme, p.nom, p.prenom, p.categorie, f.fonction, f.jour, f.pause, f.doublure, f.titulaire, f.cm, f.texte, f.statut,
         pc.trigramme, f.cm_le, f.cm_motif, pz.trigramme, f.zone_le, pr.trigramme, f.rh_le, f.rh_motif, f.cree_le,
         f.personne_id = biowanze.ma_personne(),
         (f.statut = 'en_attente' and f.personne_id <> coalesce(biowanze.ma_personne(),'00000000-0000-0000-0000-000000000000'::uuid)
          and (f.cm = biowanze.ma_trigramme() or (f.cm is null and biowanze.role_courant() in ('rh','hierarchie')))),
         (f.statut = 'confirmee' and f.doublure and f.zone_le is null and biowanze.role_courant() in ('rh','hierarchie')
          and f.personne_id <> coalesce(biowanze.ma_personne(),'00000000-0000-0000-0000-000000000000'::uuid)),
         (f.statut = 'confirmee' and (not f.doublure or f.zone_le is not null) and biowanze.role_courant() = 'rh')
  from biowanze.recyclages_fiches f
  join biowanze.personnes p on p.id = f.personne_id
  left join biowanze.comptes ccm on ccm.user_id = f.cm_par left join biowanze.personnes pc on pc.id = ccm.personne_id
  left join biowanze.comptes cz on cz.user_id = f.zone_par left join biowanze.personnes pz on pz.id = cz.personne_id
  left join biowanze.comptes crh on crh.user_id = f.rh_par left join biowanze.personnes pr on pr.id = crh.personne_id
  where biowanze.role_courant() is not null and f.statut <> 'annulee'
    and (biowanze.role_courant() in ('rh','hierarchie') or f.personne_id = biowanze.ma_personne() or f.cm = biowanze.ma_trigramme())
  order by (f.statut in ('en_attente','confirmee')) desc, f.jour desc, f.id desc
$$;

-- EN ATTENTE DE LA CONFIRMATION DU CLIENT : l'effacement réel. Le
-- connecteur Supabase demande une confirmation pour toute instruction qui
-- efface (« delete ») ; l'envoi du 22/10/2026 est resté suspendu, rien n'a
-- été appliqué. On ne contourne pas cette confirmation : ces fonctions et
-- la purge s'appliqueront quand le client l'aura donnée.
/*
create or replace function public.biowanze_annuler_demande(p_id bigint)
returns text language plpgsql security definer set search_path = '' as $$
declare d record;
begin
  select * into d from biowanze.demandes where id = p_id and personne_id = biowanze.ma_personne() and statut = 'en_attente' for update;
  if not found then raise exception 'demande introuvable ou déjà traitée'; end if;
  if d.valide_cm is not null or d.valide_rh is not null or coalesce(d.accords,'{}'::jsonb) <> '{}'::jsonb then
    raise exception 'déjà signée par une autre personne : elle ne se supprime plus';
  end if;
  delete from biowanze.notifs where demande_id = p_id and envoye_le is null;
  delete from biowanze.demandes where id = p_id;
  return 'effacee';
end $$;

create or replace function public.biowanze_modifier_demande(p_id bigint, p_formulaire text, p_lignes jsonb, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare pid uuid := biowanze.ma_personne(); d record; nid bigint;
begin
  if pid is null then raise exception 'compte non validé'; end if;
  select * into d from biowanze.demandes where id = p_id and personne_id = pid for update;
  if not found or d.statut <> 'en_attente' then raise exception 'demande introuvable ou déjà traitée'; end if;
  if d.valide_cm is not null or d.valide_rh is not null then
    raise exception 'déjà visée : elle ne se modifie plus ; annulez-la et faites-en une nouvelle';
  end if;
  delete from biowanze.notifs where demande_id = p_id and envoye_le is null;
  delete from biowanze.demandes where id = p_id;
  nid := public.biowanze_demander_formulaire(p_formulaire, p_lignes, p_texte);
  return nid;
end $$;

create or replace function public.biowanze_annuler_recyclage(p_id bigint)
returns text language plpgsql security definer set search_path = '' as $$
begin
  delete from biowanze.recyclages_fiches
   where id = p_id and personne_id = biowanze.ma_personne() and statut = 'en_attente';
  if not found then raise exception 'fiche introuvable ou déjà traitée'; end if;
  return 'effacee';
end $$;

-- et les demandes et fiches déjà annulées
delete from biowanze.notifs where envoye_le is null and demande_id in (select id from biowanze.demandes where statut = 'annulee');
delete from biowanze.demandes where statut = 'annulee';
delete from biowanze.recyclages_fiches where statut = 'annulee';
*/
