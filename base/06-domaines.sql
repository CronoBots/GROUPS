-- Seules les adresses de l'entreprise se connectent (le client, le
-- 21/10/2026 : « que seules les adresses en @biowanze.be et
-- @cropenergies.com soient prises en compte pour la vérification »).
--
-- La base est seule juge : un compte d'une autre adresse n'est jamais créé
-- (le déclencheur sur auth.users refuse l'insertion, et aucun code n'est
-- donc envoyé), et un compte existant ne peut ni changer pour une telle
-- adresse ni demander un trigramme. L'application ne fait que dire la règle
-- avant d'envoyer (DOMAINES_AUTORISES de index.html) ; si les deux listes
-- divergent, c'est celle-ci qui tranche.
--
-- ATTENTION : auth.users est celle de TOUT le projet, partagé avec PINO,
-- qui n'avait aucun compte le 21/10/2026. S'il en prend un jour, ce
-- déclencheur s'appliquera aussi à lui.

create table if not exists biowanze.domaines_autorises (domaine text primary key);
alter table biowanze.domaines_autorises enable row level security;
insert into biowanze.domaines_autorises values ('biowanze.be'), ('cropenergies.com')
  on conflict do nothing;

create or replace function biowanze.email_autorise(p_email text)
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (select 1 from biowanze.domaines_autorises
                 where domaine = lower(split_part(trim(coalesce(p_email,'')), '@', 2)))
$$;

create or replace function biowanze.refuser_domaine()
returns trigger language plpgsql security definer set search_path = '' as $$
begin
  if new.email is not null and not biowanze.email_autorise(new.email) then
    raise exception 'adresse non autorisée : seules les adresses de l''entreprise se connectent'
      using errcode = 'P0001';
  end if;
  return new;
end $$;

create or replace trigger biowanze_domaine_creation before insert on auth.users
  for each row execute function biowanze.refuser_domaine();
create or replace trigger biowanze_domaine_changement before update of email on auth.users
  for each row when (old.email is distinct from new.email)
  execute function biowanze.refuser_domaine();

-- La demande de trigramme vérifie aussi l'adresse (un compte créé avant la règle).
create or replace function public.biowanze_rattacher(p_trigramme text)
returns text language plpgsql security definer set search_path = '' as $$
declare pid uuid; deja boolean;
begin
  if auth.uid() is null then raise exception 'non connecté'; end if;
  if not biowanze.email_autorise(auth.jwt()->>'email') then
    raise exception 'adresse non autorisée : seules les adresses de l''entreprise se connectent';
  end if;
  select id into pid from biowanze.personnes where trigramme = upper(trim(p_trigramme)) and actif;
  if pid is null then raise exception 'trigramme inconnu'; end if;
  select valide into deja from biowanze.comptes where user_id = auth.uid();
  if deja then raise exception 'compte déjà validé'; end if;
  insert into biowanze.comptes(user_id, personne_id, role, email)
    values (auth.uid(), pid, 'operateur', auth.jwt()->>'email')
    on conflict (user_id) do update set personne_id = excluded.personne_id, email = excluded.email;
  return 'en_attente';
end $$;

revoke all on function biowanze.email_autorise(text) from public, anon, authenticated;
