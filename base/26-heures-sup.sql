-- LES DEMANDES DE VALIDATION D'HEURES SUPPLÉMENTAIRES (le client, le
-- 23/10/2026 : « et voici une nouvelle sorte de demande à implémenter
-- aussi », avec le formulaire « Demande de validation d'heures
-- supplémentaires », 07.12.2012 - V3).
--
-- Le formulaire papier, champ pour champ :
--   Demande du membre du personnel : nom et prénom, fonction, responsable
--   d'équipe ; la prestation : date, horaire prévu (jour / matin /
--   après-midi / nuit / jour de repos / jour de congé), durée (h, min),
--   justification — une case parmi quatre :
--     * suite à une demande explicite du responsable ;
--     * sans demande explicite du responsable direct mais travail
--       nécessaire au bon fonctionnement de l'usine (en quelques mots) ;
--     * suite à une prolongation de pause pour pallier une absence
--       imprévue (« si min. 3 h supplémentaires ont été prestées, une prime
--       de rappel sera comptabilisée ») ;
--     * suite à un rappel de (nom du responsable) ;
--   signature, date.
--   Visa du responsable hiérarchique : nom et prénom, fonction ;
--   approbation (en cas de rappel, la date à laquelle le rappel a été
--   effectué) ; restriction et sa motivation ; refus et sa motivation ;
--   signature, date.
--
-- Le circuit est celui du papier : la personne demande, le responsable
-- hiérarchique vise. Une seule signature après la sienne ; ce que la RH
-- en fait ensuite (confirmer, encoder) n'est pas sur la feuille : c'est
-- une question au client (docs/questions-client.md). La RH voit toutes
-- les demandes. Peuvent viser : le responsable d'équipe nommé sur la
-- feuille, ou à défaut la hiérarchie et la RH ; jamais sa propre demande.
-- Rien n'est écrit dans l'horaire : le classeur reste la seule source.
-- Une table à part (comme les recyclages, base/15) ; aucune suppression :
-- retirer sa demande la passe « annulée ».

create table if not exists biowanze.heures_sup (
  id bigserial primary key,
  personne_id uuid not null references biowanze.personnes(id),
  jour date not null,
  horaire text not null check (horaire in ('jour','matin','apres-midi','nuit','repos','conge')),
  minutes int not null check (minutes between 1 and 1440),
  justif text not null check (justif in ('demande','necessaire','prolongation','rappel')),
  justif_texte text,
  rappel_de text,
  responsable text,
  texte text,
  statut text not null default 'en_attente' check (statut in ('en_attente','approuvee','refusee','annulee')),
  visa_par uuid, visa_le timestamptz,
  restriction text, motivation text, rappel_le date, motif_refus text,
  cree_par uuid, cree_le timestamptz not null default now()
);
alter table biowanze.heures_sup enable row level security;
revoke all on biowanze.heures_sup from public, anon, authenticated;

create or replace function public.biowanze_demander_hs(p_jour date, p_horaire text, p_minutes int, p_justif text,
  p_justif_texte text, p_rappel_de text, p_responsable text, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare pid uuid := biowanze.ma_personne(); moi text := biowanze.ma_trigramme(); nid bigint; resp text;
begin
  if pid is null then raise exception 'compte non validé'; end if;
  -- on valide des heures déjà prestées
  if p_jour is null or p_jour > current_date or p_jour < current_date - 366 then raise exception 'date de la prestation invalide'; end if;
  if p_minutes is null or p_minutes < 1 or p_minutes > 1440 then raise exception 'durée invalide'; end if;
  if p_justif = 'necessaire' and nullif(trim(coalesce(p_justif_texte,'')),'') is null then
    raise exception 'dites en quelques mots le travail nécessaire au bon fonctionnement de l''usine';
  end if;
  if p_justif = 'rappel' and nullif(trim(coalesce(p_rappel_de,'')),'') is null then raise exception 'nommez le responsable qui vous a rappelé'; end if;
  resp := upper(nullif(trim(coalesce(p_responsable,'')),''));
  if resp is not null and not exists (select 1 from biowanze.personnes where trigramme = resp) then resp := null; end if;
  if resp = moi then resp := null; end if;
  insert into biowanze.heures_sup(personne_id, jour, horaire, minutes, justif, justif_texte, rappel_de, responsable, texte, cree_par)
    values (pid, p_jour, p_horaire, p_minutes, p_justif,
            case when p_justif = 'necessaire' then nullif(trim(coalesce(p_justif_texte,'')),'') end,
            case when p_justif = 'rappel' then nullif(trim(coalesce(p_rappel_de,'')),'') end,
            resp, nullif(trim(coalesce(p_texte,'')),''), auth.uid())
    returning id into nid;
  return nid;
end $$;

create or replace function public.biowanze_liste_hs()
returns table (id bigint, trigramme text, nom text, prenom text, categorie text, jour date, horaire text, minutes int,
               justif text, justif_texte text, rappel_de text, responsable text, texte text, statut text,
               visa_qui text, visa_le timestamptz, restriction text, motivation text, rappel_le date, motif_refus text,
               cree_le timestamptz, a_moi boolean, je_vise boolean)
language sql stable security definer set search_path = '' as $$
  select h.id, p.trigramme, p.nom, p.prenom, p.categorie, h.jour, h.horaire, h.minutes, h.justif, h.justif_texte, h.rappel_de,
         h.responsable, h.texte, h.statut, pv.trigramme, h.visa_le, h.restriction, h.motivation, h.rappel_le, h.motif_refus, h.cree_le,
         h.personne_id = biowanze.ma_personne(),
         (h.statut = 'en_attente' and h.personne_id <> coalesce(biowanze.ma_personne(),'00000000-0000-0000-0000-000000000000'::uuid)
          and (h.responsable = biowanze.ma_trigramme() or (h.responsable is null and biowanze.role_courant() in ('rh','hierarchie'))))
  from biowanze.heures_sup h
  join biowanze.personnes p on p.id = h.personne_id
  left join biowanze.comptes cv on cv.user_id = h.visa_par left join biowanze.personnes pv on pv.id = cv.personne_id
  where biowanze.role_courant() is not null and h.statut <> 'annulee'
    and (biowanze.role_courant() in ('rh','hierarchie') or h.personne_id = biowanze.ma_personne() or h.responsable = biowanze.ma_trigramme())
  order by (h.statut = 'en_attente') desc, h.jour desc, h.id desc
$$;

create or replace function public.biowanze_viser_hs(p_id bigint, p_ok boolean, p_restriction text, p_motivation text, p_rappel_le date)
returns text language plpgsql security definer set search_path = '' as $$
declare h record; moi text := biowanze.ma_trigramme(); r biowanze.role := biowanze.role_courant();
begin
  select * into h from biowanze.heures_sup where id = p_id for update;
  if not found or h.statut <> 'en_attente' then raise exception 'demande introuvable ou déjà traitée'; end if;
  if h.personne_id = biowanze.ma_personne() then raise exception 'on ne vise pas sa propre demande'; end if;
  if r is null or not (coalesce(h.responsable = moi, false) or r in ('rh','hierarchie')) then raise exception 'réservé au responsable hiérarchique'; end if;
  if not p_ok and nullif(trim(coalesce(p_motivation,'')),'') is null then raise exception 'un refus se motive'; end if;
  if p_ok and nullif(trim(coalesce(p_restriction,'')),'') is not null and nullif(trim(coalesce(p_motivation,'')),'') is null then
    raise exception 'une restriction se motive';
  end if;
  if p_ok and h.justif = 'rappel' and p_rappel_le is null then raise exception 'en cas de rappel, la date du rappel est à donner'; end if;
  update biowanze.heures_sup set statut = case when p_ok then 'approuvee' else 'refusee' end,
         visa_par = auth.uid(), visa_le = now(),
         restriction = case when p_ok then nullif(trim(coalesce(p_restriction,'')),'') end,
         motivation = case when p_ok then nullif(trim(coalesce(p_motivation,'')),'') end,
         motif_refus = case when not p_ok then nullif(trim(coalesce(p_motivation,'')),'') end,
         rappel_le = case when p_ok then p_rappel_le end
   where id = p_id;
  return case when p_ok then 'approuvee' else 'refusee' end;
end $$;

create or replace function public.biowanze_annuler_hs(p_id bigint)
returns text language plpgsql security definer set search_path = '' as $$
begin
  update biowanze.heures_sup set statut = 'annulee'
   where id = p_id and personne_id = biowanze.ma_personne() and statut = 'en_attente';
  if not found then raise exception 'demande introuvable ou déjà traitée'; end if;
  return 'annulee';
end $$;

-- les notifications, par la file commune (base/14)
create or replace function biowanze.hs_notifier()
returns trigger language plpgsql security definer set search_path = '' as $$
declare dem text; quoi text; n int := 0; u text := './?vue=heures';
begin
  select trigramme into dem from biowanze.personnes where id = new.personne_id;
  quoi := (new.minutes / 60)||' h'||case when new.minutes % 60 > 0 then ' '||lpad((new.minutes % 60)::text,2,'0') else '' end
          ||' le '||to_char(new.jour,'DD/MM');
  if tg_op = 'INSERT' then
    if new.responsable is not null then
      insert into biowanze.notifs(tri, titre, texte, url) values (new.responsable, 'Heures supplémentaires à viser',
        coalesce(dem,'?')||' : '||quoi||'. Touchez pour viser.', u);
    else
      insert into biowanze.notifs(tri, titre, texte, url) select distinct p.trigramme, 'Heures supplémentaires à viser',
        coalesce(dem,'?')||' : '||quoi||'.', u
        from biowanze.comptes c join biowanze.personnes p on p.id = c.personne_id
       where c.role in ('rh','hierarchie') and c.valide and p.trigramme is not null and p.trigramme is distinct from dem;
    end if;
    n := 1;
  elsif new.statut is distinct from old.statut and new.statut in ('approuvee','refusee') and dem is not null then
    insert into biowanze.notifs(tri, titre, texte, url) values (dem,
      case new.statut when 'approuvee' then 'Heures supplémentaires approuvées' else 'Heures supplémentaires refusées' end,
      'Votre demande ('||quoi||') est '||case new.statut when 'approuvee' then 'approuvée'||coalesce(', avec restriction : '||new.restriction,'')
        else 'refusée'||coalesce(' : '||new.motif_refus,'') end||'.', u);
    n := 1;
  end if;
  if n > 0 then perform biowanze.lancer_notifs(); end if;
  return new;
end $$;
revoke all on function biowanze.hs_notifier() from public, anon, authenticated;
create or replace trigger hs_notifier after insert or update of statut on biowanze.heures_sup
  for each row execute function biowanze.hs_notifier();

revoke all on function public.biowanze_demander_hs(date,text,int,text,text,text,text,text) from public, anon;
revoke all on function public.biowanze_liste_hs() from public, anon;
revoke all on function public.biowanze_viser_hs(bigint,boolean,text,text,date) from public, anon;
revoke all on function public.biowanze_annuler_hs(bigint) from public, anon;
grant execute on function public.biowanze_demander_hs(date,text,int,text,text,text,text,text) to authenticated;
grant execute on function public.biowanze_liste_hs() to authenticated;
grant execute on function public.biowanze_viser_hs(bigint,boolean,text,text,date) to authenticated;
grant execute on function public.biowanze_annuler_hs(bigint) to authenticated;
