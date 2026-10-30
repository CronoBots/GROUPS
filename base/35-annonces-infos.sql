-- LES ANNONCES ET LES INFOS PRATIQUES DE L'USINE (le client, le 30/10/2026 :
-- « tu peux faire toutes les améliorations que tu as proposées »). Un fil
-- d'annonces (arrêt technique, audit, consigne) et des pages fixes (en cas
-- de maladie, numéros utiles, délais des congés, règlement de travail) que
-- la RH rédige dans l'application ; tout compte validé les lit. Rien n'est
-- public : l'application exige déjà un compte validé.
--
-- Rien n'y est supprimé ni remplacé : elle s'applique par le connecteur
-- (CLAUDE.md, sur les migrations qui suppriment).

create table if not exists biowanze.contenus (
  id bigserial primary key,
  genre text not null check (genre in ('annonce','info')),
  titre text not null check (length(btrim(titre)) between 1 and 120),
  corps text not null check (length(btrim(corps)) between 1 and 4000),
  rubrique text check (rubrique is null or length(rubrique) <= 40),
  ordre int not null default 0,
  epingle boolean not null default false,
  jusquau date,                         -- une annonce échue ne se lit plus
  auteur text,                          -- le trigramme de la RH qui a écrit
  cree_le timestamptz not null default now(),
  maj_le timestamptz not null default now()
);
alter table biowanze.contenus enable row level security;
revoke all on biowanze.contenus from public, anon, authenticated;
revoke all on sequence biowanze.contenus_id_seq from public, anon, authenticated;

-- Lire : tout compte validé ; les annonces échues ne reviennent plus.
create or replace function public.biowanze_contenus()
returns table (id bigint, genre text, titre text, corps text, rubrique text, ordre int,
               epingle boolean, jusquau date, auteur text, cree_le timestamptz, maj_le timestamptz)
language plpgsql stable security definer set search_path = '' as $$
begin
  if biowanze.role_courant() is null then raise exception 'compte non validé'; end if;
  return query
    select c.id, c.genre, c.titre, c.corps, c.rubrique, c.ordre, c.epingle, c.jusquau, c.auteur, c.cree_le, c.maj_le
      from biowanze.contenus c
     where c.genre = 'info' or c.jusquau is null or c.jusquau >= (now() at time zone 'Europe/Brussels')::date
     order by c.genre, c.epingle desc, c.ordre, c.cree_le desc;
end $$;
revoke all on function public.biowanze_contenus() from public, anon;
grant execute on function public.biowanze_contenus() to authenticated;

-- Écrire (créer si p_id est nul, sinon modifier) : la RH seule. Une annonce
-- peut prévenir tout le monde : la file des notifications (base/14) reçoit
-- une ligne « * », que tools/notifier-demandes.js envoie à tous les abonnés.
create or replace function public.biowanze_ecrire_contenu(
  p_id bigint, p_genre text, p_titre text, p_corps text, p_rubrique text,
  p_ordre int, p_epingle boolean, p_jusquau date, p_notifier boolean)
returns bigint language plpgsql security definer set search_path = '' as $$
declare v_id bigint; t text := btrim(coalesce(p_titre,'')); c text := btrim(coalesce(p_corps,''));
begin
  if biowanze.role_courant() is distinct from 'rh' then raise exception 'réservé à la RH'; end if;
  if p_genre not in ('annonce','info') then raise exception 'genre inconnu'; end if;
  if length(t) not between 1 and 120 then raise exception 'titre de 1 à 120 caractères'; end if;
  if length(c) not between 1 and 4000 then raise exception 'texte de 1 à 4 000 caractères'; end if;
  if p_id is null then
    insert into biowanze.contenus(genre, titre, corps, rubrique, ordre, epingle, jusquau, auteur)
    values (p_genre, t, c, nullif(btrim(coalesce(p_rubrique,'')),''), coalesce(p_ordre,0),
            coalesce(p_epingle,false), p_jusquau, biowanze.ma_trigramme())
    returning id into v_id;
  else
    update biowanze.contenus set titre = t, corps = c, rubrique = nullif(btrim(coalesce(p_rubrique,'')),''),
           ordre = coalesce(p_ordre,0), epingle = coalesce(p_epingle,false), jusquau = p_jusquau,
           auteur = biowanze.ma_trigramme(), maj_le = now()
     where id = p_id and genre = p_genre
    returning id into v_id;
    if v_id is null then raise exception 'contenu introuvable'; end if;
  end if;
  if p_genre = 'annonce' and coalesce(p_notifier,false) then
    insert into biowanze.notifs(tri, titre, texte, url)
    values ('*', t, left(regexp_replace(c, '\s+', ' ', 'g'), 180), './?vue=aide');
    perform biowanze.lancer_notifs();
  end if;
  return v_id;
end $$;
revoke all on function public.biowanze_ecrire_contenu(bigint,text,text,text,text,int,boolean,date,boolean) from public, anon;
grant execute on function public.biowanze_ecrire_contenu(bigint,text,text,text,text,int,boolean,date,boolean) to authenticated;

-- Effacer : la RH seule.
create or replace function public.biowanze_effacer_contenu(p_id bigint)
returns void language plpgsql security definer set search_path = '' as $$
begin
  if biowanze.role_courant() is distinct from 'rh' then raise exception 'réservé à la RH'; end if;
  delete from biowanze.contenus where id = p_id;
  if not found then raise exception 'contenu introuvable'; end if;
end $$;
revoke all on function public.biowanze_effacer_contenu(bigint) from public, anon;
grant execute on function public.biowanze_effacer_contenu(bigint) to authenticated;
