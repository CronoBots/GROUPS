-- LE REMPLAÇANT D'ABORD, LA RH ENSUITE (le client, le 22/10/2026 : « si sur
-- la demande de congé le travailleur sélectionne un remplaçant, ce même
-- remplaçant doit recevoir la demande sur son téléphone pour signer le
-- remplacement ; et la RH ne doit recevoir la demande qu'une fois le
-- remplacement signé »).
--
--  1. biowanze.notifs : la file des notifications du téléphone, fermée au
--     public. Un déclencheur sur biowanze.demandes la remplit :
--       - une demande avec remplaçant(s) → chaque remplaçant ;
--       - une demande sans remplaçant → les comptes RH ;
--       - la DERNIÈRE signature d'un remplaçant → les comptes RH, et le
--         demandeur (« votre remplaçant a signé »).
--     puis lance aussitôt l'action GitHub « notifier.yml » (le jeton est
--     celui de biowanze_lancer_horaire, dans le coffre). Le robot lit la file
--     par biowanze_notifs_a_envoyer(clé) et envoie par web-push : la clé
--     privée d'envoi ne quitte pas les secrets GitHub.
--  2. « attend_rh » ne vaut vrai qu'une fois tous les remplaçants signés :
--     la demande n'est « à traiter » pour la RH qu'à ce moment.
--  3. Une garde dans la base : la RH ne peut accepter ni refuser une
--     demande dont un remplaçant n'a pas signé (l'écran n'est pas la règle).
--     La hiérarchie, le client n'en a rien dit : elle garde son circuit.

create or replace function biowanze.accords_complets(p_lignes jsonb, p_accords jsonb)
returns boolean language sql immutable set search_path = '' as $$
  select not exists (select 1 from jsonb_array_elements(coalesce(p_lignes,'[]'::jsonb)) x
                     where coalesce(x->>'rp','') <> '' and not (coalesce(p_accords,'{}'::jsonb) ? (x->>'rp')))
$$;
revoke all on function biowanze.accords_complets(jsonb,jsonb) from public, anon, authenticated;

create table if not exists biowanze.notifs (
  id bigserial primary key,
  tri text not null,
  titre text not null,
  texte text not null,
  url text not null default './?vue=demandes',
  demande_id bigint,
  cree_le timestamptz not null default now(),
  envoye_le timestamptz
);
alter table biowanze.notifs enable row level security;
revoke all on biowanze.notifs from public, anon, authenticated;
create index if not exists notifs_a_envoyer on biowanze.notifs (cree_le) where envoye_le is null;

-- lancer l'envoi tout de suite ; une notification manquée ne bloque jamais
-- une demande (l'action repasse aussi toutes les 30 minutes)
create or replace function biowanze.lancer_notifs()
returns void language plpgsql security definer set search_path = '' as $$
declare jeton text;
begin
  select decrypted_secret into jeton from vault.decrypted_secrets where name = 'biowanze_github' limit 1;
  if coalesce(jeton,'') = '' then return; end if;
  perform net.http_post(
    url := 'https://api.github.com/repos/CronoBots/GROUPS/actions/workflows/notifier.yml/dispatches',
    body := '{"ref":"main"}'::jsonb,
    headers := jsonb_build_object('Authorization','Bearer '||jeton,'Accept','application/vnd.github+json',
      'X-GitHub-Api-Version','2022-11-28','User-Agent','biowanze-notifs','Content-Type','application/json'));
exception when others then null;
end $$;
revoke all on function biowanze.lancer_notifs() from public, anon, authenticated;

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
    if tg_op = 'UPDATE' and dem is not null then
      insert into biowanze.notifs(tri, titre, texte, demande_id)
        values (dem, 'Remplacement signé', 'Votre remplaçant a signé votre demande '||per||' : elle part chez la RH.', new.id);
    end if;
  end if;
  if n > 0 then perform biowanze.lancer_notifs(); end if;
  return new;
end $$;
revoke all on function biowanze.demandes_notifier() from public, anon, authenticated;
create trigger demandes_notifier after insert or update of accords on biowanze.demandes
  for each row execute function biowanze.demandes_notifier();

create or replace function biowanze.demandes_garde_rh()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if biowanze.role_courant() = 'rh' and old.statut = 'en_attente'
     and ((new.valide_rh is not null and old.valide_rh is null) or new.statut in ('acceptee','refusee'))
     and not biowanze.accords_complets(new.lignes, new.accords) then
    raise exception 'le remplaçant n''a pas encore signé : la demande arrive chez la RH après sa signature';
  end if;
  return new;
end $$;
revoke all on function biowanze.demandes_garde_rh() from public, anon, authenticated;
create trigger demandes_garde_rh before update on biowanze.demandes
  for each row execute function biowanze.demandes_garde_rh();

-- (appliqué le 22/10/2026 morceau par morceau, SANS « drop trigger » : le
-- connecteur demande une confirmation pour toute suppression, et l'envoi
-- restait suspendu ; les déclencheurs n'existaient pas encore.)

-- le robot lit la file (et la marque envoyée) avec la clé partagée
create or replace function public.biowanze_notifs_a_envoyer(p_cle text)
returns table (tri text, titre text, texte text, url text)
language plpgsql security definer set search_path = '' as $$
begin
  if not biowanze.cle_robot(p_cle) then raise exception 'clé refusée'; end if;
  return query
    update biowanze.notifs n set envoye_le = now()
     where n.envoye_le is null and n.cree_le > now() - interval '2 days'
    returning n.tri, n.titre, n.texte, n.url;
end $$;
revoke all on function public.biowanze_notifs_a_envoyer(text) from public;
grant execute on function public.biowanze_notifs_a_envoyer(text) to anon, authenticated;

-- la liste : « attend_rh » une fois les remplaçants signés (12-formulaires.sql, une ligne changée)
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
  where biowanze.role_courant() is not null
    and (biowanze.role_courant() in ('rh','hierarchie') or d.personne_id = biowanze.ma_personne()
         or exists (select 1 from jsonb_array_elements(d.lignes) x where x->>'rp' = biowanze.ma_trigramme()))
  order by (d.statut = 'en_attente') desc, d.du, d.id
$$;
