atendimentos = """
    SELECT ia.NUATENDIMENTO, ia.NUITEM, ia.DEATENDIMENTO, pr.NUORDEM, ra.DTREGISTRO, 
    coalesce((SELECT sum(aa.QTHORASREAL) FROM sac.ESACATIVIDADE AA
        WHERE AA.CDPROJETO = IA.CDPROJETO
        AND AA.NUATENDIMENTO = IA.NUATENDIMENTO
        AND AA.NUITEM = IA.NUITEM),0) as QTHORASREAL, COALESCE(ia.DESOLUCAO, '') AS DESOLUCAO
      FROM sac.ESACREGISTROATEND ra
      JOIN sac.ESACITEMATEND ia
        ON ia.cdProjeto = ia.CDPROJETO
       AND ia.NUATENDIMENTO = ra.NUATENDIMENTO  
      JOIN sac.ESACPRIORIDADE pr
        ON pr.cdPrioridade = ia.cdPrioridade
     WHERE ra.cdProjeto = 3
       AND ia.CDPROJETO = 3
       AND ra.CDSISTEMA IN (31,93)
       AND length(RTRIM(ia.DEATENDIMENTO)) >= 30 
    """

atendimentos_filtro = " AND ia.NUATENDIMENTO = {} AND ia.NUITEM = {}"

atendimentos_data = " AND VARCHAR_FORMAT (ra.DTREGISTRO,'YYYY-MM-DD') > '{}'"

atendimentos_order = " ORDER BY ra.DTREGISTRO DESC"

pessoas = """
        SELECT ia.NUATENDIMENTO, ia.NUITEM, aa.CDUSUARIO, count(1) AS QUANT
          FROM sac.ESACREGISTROATEND ra
          JOIN sac.ESACITEMATEND ia
            ON ia.cdProjeto = ia.CDPROJETO
           AND ia.NUATENDIMENTO = ra.NUATENDIMENTO  
          JOIN sac.ESACPRIORIDADE pr
            ON pr.cdPrioridade = ia.cdPrioridade
          JOIN sac.ESACATIVIDADE AA
            ON AA.CDPROJETO = IA.CDPROJETO
           AND AA.NUATENDIMENTO = IA.NUATENDIMENTO
           AND AA.NUITEM = IA.NUITEM
         WHERE ra.cdProjeto = 3
           AND ia.CDPROJETO = 3
           AND ra.CDSISTEMA IN (31,93)
           AND aa.CDUSUARIO NOT IN ('PORTALCLIENTE', 'AUTOMATIZACAO_PORTAL')
        """

pessoas_group = " GROUP BY ia.NUATENDIMENTO, ia.NUITEM, aa.CDUSUARIO"
