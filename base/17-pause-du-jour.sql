-- LA PAUSE QU'ON FAIT VRAIMENT (le client, le 22/10/2026 : « pour les
-- demandes de congé, la pause qui s'indique dans ma colonne est la pause
-- normale du cycle et non celle que je fais vraiment »).
--
-- La cellule du classeur dit la pause PRÉVUE par le cycle ; une annotation
-- qui écrit une pause ou une plage horaire dit celle qui sera prestée, et
-- elle prime (la règle de tête du projet) : un échange ["N","PM"] est une
-- PM, un rappel ["-","AM"] une AM — et non plus « un repos : rien à
-- modifier ». Un congé, un atelier, « R » en annotation laissent la
-- cellule. Même lecture que dmPrevue() dans index.html (grFamille « poste ») :
-- les codes de la famille « poste », AM/PM/N/D/-, « H. flott. », une plage
-- « 6h-14h ».

create or replace function biowanze.pause_du_jour(p_personne uuid, p_jour date)
returns text language sql stable security definer set search_path = '' as $$
  select case
    when nullif(trim(j.annotation),'') is not null and (
         exists (select 1 from biowanze.codes c where c.code = trim(j.annotation) and c.famille = 'poste')
         or trim(j.annotation) ~* '^(AM|PM|N|D|-)$'
         or trim(j.annotation) ~* '^h\.?\s*flot'
         or regexp_replace(j.annotation, '\s+', '', 'g') ~ '^\d{1,2}h(\d{2})?-\d{1,2}h(\d{2})?$')
    then trim(j.annotation) else j.cellule end
  from biowanze.journees j where j.personne_id = p_personne and j.jour = p_jour
$$;
revoke all on function biowanze.pause_du_jour(uuid,date) from public, anon, authenticated;

-- le formulaire, deux lignes changées (12-formulaires.sql)
create or replace function public.biowanze_demander_formulaire(p_formulaire text, p_lignes jsonb, p_texte text)
returns bigint language plpgsql security definer set search_path = '' as $$
declare pid uuid := biowanze.ma_personne(); moi text := biowanze.ma_trigramme();
        l jsonb; j date; propres jsonb := '[]'; vus date[] := '{}'; n int := 0; npause int := 0; nday int := 0;
        prevue text; rp text; rpid uuid; dmin date; dmax date; nid bigint; code1 text;
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
