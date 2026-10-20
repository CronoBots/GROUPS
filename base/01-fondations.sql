-- BIOWANZE, étape 2 : la base de l'horaire (décision du client du 20/10/2026).
-- Appliquée au projet Supabase « PINO » dans un schéma à part, `biowanze`,
-- jamais exposé à l'API : l'application n'y accède que par des fonctions
-- public.biowanze_* qui vérifient le rôle de l'appelant. Aucune donnée ici :
-- ce fichier ne porte que la structure.
create schema if not exists biowanze;
revoke all on schema biowanze from public, anon, authenticated;

create type biowanze.role as enum ('rh','hierarchie','operateur');

-- Les personnes : le trigramme est la clé que l'application connaît déjà.
create table biowanze.personnes (
  id uuid primary key default gen_random_uuid(),
  trigramme text not null unique,
  nom text, prenom text, matricule text,
  categorie text,                -- « Shift 3 », « Contremaîtres de production »…
  statut text,                   -- Employé, Ouvrier, Intérimaire
  actif boolean not null default true,
  cree_le timestamptz not null default now(),
  maj_le timestamptz not null default now()
);

-- Les comptes : un utilisateur de connexion, une personne, un rôle.
create table biowanze.comptes (
  user_id uuid primary key references auth.users(id) on delete cascade,
  personne_id uuid references biowanze.personnes(id) on delete set null,
  role biowanze.role not null default 'operateur',
  cree_le timestamptz not null default now()
);

-- Les journées, telles que le classeur les écrit : la cellule (poste
-- prévu), l'annotation, le commentaire. « source » dit d'où vient la ligne :
-- le classeur (synchronisé) ou une saisie dans l'application.
create table biowanze.journees (
  personne_id uuid not null references biowanze.personnes(id) on delete cascade,
  jour date not null,
  cellule text, annotation text, commentaire text,
  source text not null default 'classeur' check (source in ('classeur','saisie')),
  maj_par uuid references auth.users(id),
  maj_le timestamptz not null default now(),
  primary key (personne_id, jour)
);

-- Les événements structurés, qui remplaceront le texte libre.
create type biowanze.type_evenement as enum
  ('remplacement','echange','rappel','conge','maladie','formation','syndical',
   'flex_plus','flex_moins','arrivee','depart','atelier','note');
create table biowanze.evenements (
  id bigint generated always as identity primary key,
  personne_id uuid not null references biowanze.personnes(id) on delete cascade,
  jour date not null,
  type biowanze.type_evenement not null,
  autre_id uuid references biowanze.personnes(id),   -- remplacé, échangé avec…
  debut time, fin time, heures numeric(5,2),
  code text,                                          -- VA, RTT, RHS, atelier…
  texte text,
  auteur uuid references auth.users(id),
  cree_le timestamptz not null default now(),
  annule_le timestamptz, annule_par uuid references auth.users(id)
);
create index on biowanze.evenements (personne_id, jour);

-- Les demandes des opérateurs : validées par le contremaître ET la RH
-- (le client, le 20/10/2026).
create table biowanze.demandes (
  id bigint generated always as identity primary key,
  personne_id uuid not null references biowanze.personnes(id) on delete cascade,
  type text not null check (type in ('conge','echange','autre')),
  du date not null, au date not null,
  code text, autre_id uuid references biowanze.personnes(id), texte text,
  statut text not null default 'en_attente' check (statut in ('en_attente','acceptee','refusee','annulee')),
  valide_cm uuid references auth.users(id), valide_cm_le timestamptz,
  valide_rh uuid references auth.users(id), valide_rh_le timestamptz,
  motif_refus text,
  cree_par uuid references auth.users(id),
  cree_le timestamptz not null default now()
);

-- Les polyvalences.
create table biowanze.polyvalences (
  personne_id uuid not null references biowanze.personnes(id) on delete cascade,
  atelier text not null,
  degre text, depuis date, fin date, texte text,
  primary key (personne_id, atelier)
);

-- L'HISTORIQUE : chaque écriture, avant et après, son auteur et son heure.
create table biowanze.historique (
  id bigint generated always as identity primary key,
  table_nom text not null, operation text not null,
  avant jsonb, apres jsonb,
  auteur uuid, quand timestamptz not null default now()
);
create or replace function biowanze.tracer() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  -- Les journées venues du classeur ne se tracent pas (des milliers à chaque
  -- synchronisation) : seules les saisies le sont.
  if tg_table_name = 'journees' then
    if tg_op = 'DELETE' then
      if old.source <> 'saisie' then return old; end if;
    elsif new.source <> 'saisie' then
      return new;
    end if;
  end if;
  insert into biowanze.historique(table_nom, operation, avant, apres, auteur)
  values (tg_table_name, tg_op,
          case when tg_op in ('UPDATE','DELETE') then to_jsonb(old) end,
          case when tg_op in ('INSERT','UPDATE') then to_jsonb(new) end,
          auth.uid());
  return coalesce(new, old);
end $$;
create trigger tracer after insert or update or delete on biowanze.personnes for each row execute function biowanze.tracer();
create trigger tracer after insert or update or delete on biowanze.comptes for each row execute function biowanze.tracer();
create trigger tracer after insert or update or delete on biowanze.journees for each row execute function biowanze.tracer();
create trigger tracer after insert or update or delete on biowanze.evenements for each row execute function biowanze.tracer();
create trigger tracer after insert or update or delete on biowanze.demandes for each row execute function biowanze.tracer();
create trigger tracer after insert or update or delete on biowanze.polyvalences for each row execute function biowanze.tracer();

-- Défense en profondeur : RLS partout, aucune règle ouverte. Seules les
-- fonctions (security definer) lisent et écrivent.
alter table biowanze.personnes enable row level security;
alter table biowanze.comptes enable row level security;
alter table biowanze.journees enable row level security;
alter table biowanze.evenements enable row level security;
alter table biowanze.demandes enable row level security;
alter table biowanze.polyvalences enable row level security;
alter table biowanze.historique enable row level security;

-- Le rôle de l'appelant (null s'il n'a pas de compte).
create or replace function biowanze.role_courant() returns biowanze.role
language sql stable security definer set search_path = '' as $$
  select role from biowanze.comptes where user_id = auth.uid()
$$;
revoke all on function biowanze.role_courant() from public, anon, authenticated;
revoke all on function biowanze.tracer() from public, anon, authenticated;
