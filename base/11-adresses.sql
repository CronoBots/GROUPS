-- Une adresse précise peut être admise hors des domaines de l'entreprise
-- (le client, le 21/10/2026 : « pour VBN, envoie le code sur mon mail du
-- robot »). Les codes partis vers Outlook n'arrivaient plus ; ceux partis
-- vers Gmail arrivent. La liste vit dans la base SEULE : ce fichier n'y
-- inscrit aucune adresse (le dépôt est public). On l'alimente à la main :
--
--   insert into biowanze.adresses_autorisees values ('…', 'raison');
--
-- L'application n'en a pas de copie : pour une adresse hors des domaines,
-- elle tente l'envoi et c'est la base qui accepte ou refuse.

create table if not exists biowanze.adresses_autorisees (
  email text primary key check (email = lower(trim(email))),
  raison text not null
);
alter table biowanze.adresses_autorisees enable row level security;

create or replace function biowanze.email_autorise(p_email text)
returns boolean language sql stable security definer set search_path = '' as $$
  select exists (select 1 from biowanze.domaines_autorises
                 where domaine = lower(split_part(trim(coalesce(p_email,'')), '@', 2)))
      or exists (select 1 from biowanze.adresses_autorisees
                 where email = lower(trim(coalesce(p_email,''))))
$$;

revoke all on function biowanze.email_autorise(text) from public, anon, authenticated;
