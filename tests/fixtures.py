import datetime
from ark import Ark

issues = {
    'metadata': {
        'listType': 'years',
        'parentArk': Ark("cb32707911p", naan="12148", qualifier="date"),
        'totalIssues': 157,
        'uc3': 'no'
        },
    'year_list': [1899, 1900, 1901, 1902],
    'issue_list': []
    }

issues_1902 = {
    "metadata": {
        "date": 1902,
        "listType": "issue",
        "parentArk": Ark.parse("ark:/12148/cb32707911p/date"),
    },
    "year_list": [],
    "issue_list": [
        {"metadata": {"ark": Ark("bpt6k45421002"), "dayOfYear": 6}, "text": "06 janvier 1902"},
        {"metadata": {"ark": Ark("bpt6k4542101g"), "dayOfYear": 12}, "text": "12 janvier 1902"},
        {"metadata": {"ark": Ark("bpt6k4542102w"), "dayOfYear": 19}, "text": "19 janvier 1902"},
        {"metadata": {"ark": Ark("bpt6k45421039"), "dayOfYear": 26}, "text": "26 janvier 1902"},
        {"metadata": {"ark": Ark("bpt6k4542104q"), "dayOfYear": 33}, "text": "02 février 1902"},
        {"metadata": {"ark": Ark("bpt6k45421054"), "dayOfYear": 40}, "text": "09 février 1902"},
        {"metadata": {"ark": Ark("bpt6k4542106j"), "dayOfYear": 47}, "text": "16 février 1902"},
        {"metadata": {"ark": Ark("bpt6k4542107z"), "dayOfYear": 54}, "text": "23 février 1902"},
        {"metadata": {"ark": Ark("bpt6k4542108c"), "dayOfYear": 61}, "text": "02 mars 1902"},
        {"metadata": {"ark": Ark("bpt6k4542109s"), "dayOfYear": 68}, "text": "09 mars 1902"},
        {"metadata": {"ark": Ark("bpt6k4542110f"), "dayOfYear": 75}, "text": "16 mars 1902"},
        {"metadata": {"ark": Ark("bpt6k4542111v"), "dayOfYear": 82}, "text": "23 mars 1902"},
        {"metadata": {"ark": Ark("bpt6k45421128"), "dayOfYear": 89}, "text": "30 mars 1902"},
        {"metadata": {"ark": Ark("bpt6k4542113p"), "dayOfYear": 96}, "text": "06 avril 1902"},
        {"metadata": {"ark": Ark("bpt6k45421143"), "dayOfYear": 103}, "text": "13 avril 1902"},
        {"metadata": {"ark": Ark("bpt6k4542115h"), "dayOfYear": 110}, "text": "20 avril 1902"},
        {"metadata": {"ark": Ark("bpt6k4542116x"), "dayOfYear": 117}, "text": "27 avril 1902"},
        {"metadata": {"ark": Ark("bpt6k4542117b"), "dayOfYear": 124}, "text": "04 mai 1902"},
        {"metadata": {"ark": Ark("bpt6k4542118r"), "dayOfYear": 132}, "text": "12 mai 1902"},
        {"metadata": {"ark": Ark("bpt6k45421195"), "dayOfYear": 138}, "text": "18 mai 1902"},
        {"metadata": {"ark": Ark("bpt6k4542120t"), "dayOfYear": 145}, "text": "25 mai 1902"},
        {"metadata": {"ark": Ark("bpt6k45421217"), "dayOfYear": 152}, "text": "01 juin 1902"},
        {"metadata": {"ark": Ark("bpt6k4542122n"), "dayOfYear": 159}, "text": "08 juin 1902"},
        {"metadata": {"ark": Ark("bpt6k45421232"), "dayOfYear": 166}, "text": "15 juin 1902"},
        {"metadata": {"ark": Ark("bpt6k4542124g"), "dayOfYear": 173}, "text": "22 juin 1902"},
        {"metadata": {"ark": Ark("bpt6k4542125w"), "dayOfYear": 180}, "text": "29 juin 1902"},
        {"metadata": {"ark": Ark("bpt6k45421269"), "dayOfYear": 187}, "text": "06 juillet 1902"},
        {"metadata": {"ark": Ark("bpt6k4542127q"), "dayOfYear": 194}, "text": "13 juillet 1902"},
        {"metadata": {"ark": Ark("bpt6k45421284"), "dayOfYear": 201}, "text": "20 juillet 1902"},
        {"metadata": {"ark": Ark("bpt6k4542129j"), "dayOfYear": 208}, "text": "27 juillet 1902"},
        {"metadata": {"ark": Ark("bpt6k45421306"), "dayOfYear": 215}, "text": "03 août 1902"},
        {"metadata": {"ark": Ark("bpt6k4542131m"), "dayOfYear": 222}, "text": "10 août 1902"},
        {"metadata": {"ark": Ark("bpt6k45421321"), "dayOfYear": 229}, "text": "17 août 1902"},
    ],
}

oairecord = {
    'visibility_rights': 'all', 
    'title': 'La plage d\'Etretat par l\'auteur de "Monsieur X et Mme ***"', 
    'typedoc': 'monographie', 
    'provenance': 'bnf.fr', 
    'dewey': 8, 
    'sdewey': 84,
    'nqamoyen': 92.57, 
    'date': [1868, 1868], 
    'mode_indexation': 'text', 
    'source': 'Bibliothèque nationale de France, département Littérature et art, Y2-59413', 
    'first_indexation_date': datetime.datetime(2010, 5, 3, 0, 0), 
    'metadata': {
        'countResults': 1, 
        'resultType': 'CVOAIRecordSearchService', 
        'searchTime': ''}
    }

pagination = {'structure': {'firstDisplayedPage': 1, 'hasToc': True, 'TocLocation': 0, 'hasContent': True, 'idUPN': True, 'nbVueImages': 1}, 'page_list': [{'numero': True, 'ordre': 1, 'pagination_type': True, 'image_width': 15316, 'image_height': 9998}]}


contentsearch_onepage = {'metadata': {'countResults': 1}, 'items': [{'page': 5, 'page_height': 2488, 'page_width': 1430, 'altoid': {'countResults': 1, 'altoidstring': [{'PAG_00000005_ST000039': {'height': 35, 'highlightStyle': 0, 'hpos': 334, 'vpos': 573, 'width': 176}}]}}], 'query': 'intimider'}
contentsearch_allpages = {'metadata': {'countResults': 1}, 'items': [{'page': 5, 'text': ['Quelques membres plus experts ne se laissèrent point intimider par ces menaces chimériques']}], 'query': 'intimider'}


toc = """<TEI.2 xmlns:xlink="http://www.w3.org/TR/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://bibnum.bnf.fr/ns/tdmNum.xsd">
<text id="tdm.0165680">
<body>
<div0 type="TdM">
<head>TABLE DES CHAPITRES</head>
<div1>
<head>
<hi rend="italic">Figures disparues.</hi>
</head>
<table>
<row>
<cell>
<seg n="int.000001">I. - Un curieux amateur «le peinture</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000008.TIF)" n="lie.000001" type="image">9</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000002">II. - Un propriétaire de la Tour Saint-Jacques</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000029.TIF)" n="lie.000002" type="image">30</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000003">III. - Courbet et la colonne Vendôme</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000064.TIF)" n="lie.000003" type="image">65</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000004">IV. - Le poète Germain Nouveau</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000073.TIF)" n="lie.000004" type="image">74</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000005">V. - Guillaume Apollinaire, historien de<placeName>Paris</placeName>.</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000083.TIF)" n="lie.000005" type="image">84</xref>
</cell>
</row>
</table>
</div1>
<div1>
<head>
<placeName>Promenades parisiennes.</placeName>
</head>
<table>
<row>
<cell>
<seg n="int.000006">I. - Rendez-vous d'artistes</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000100.TIF)" n="lie.000006" type="image">101</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000007">II. - Richesses inconnues</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000120.TIF)" n="lie.000007" type="image">121</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000008">III. - Un coin de boulevard</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000148.TIF)" n="lie.000008" type="image">149</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000009">IV. - Le dernier logis de Scribe</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000159.TIF)" n="lie.000009" type="image">160</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000010">V. - Sur le quai du Louvre</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000166.TIF)" n="lie.000010" type="image">167</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000011">VI. - Un cabaret de conspirateurs</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000176.TIF)" n="lie.000011" type="image">177</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000012">VII. - Un bateau-lavoir historique</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000184.TIF)" n="lie.000012" type="image">185</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000013">VIII. - Autour de l'église Saint-Gervais</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000194.TIF)" n="lie.000013" type="image">195</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000014">IX. - Fouilles parisiennes</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000205.TIF)" n="lie.000014" type="image">206</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000015">X. - Le quartier des jouets</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000214.TIF)" n="lie.000015" type="image">215</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000016">XI . - Le château de<placeName>Conflans</placeName></seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000230.TIF)" n="lie.000016" type="image">231</xref>
</cell>
</row>
</table>
</div1>
<div1>
<head>
<hi rend="italic">Paris d'autrefois.</hi>
</head>
<table>
<row>
<cell>
<seg n="int.000017">I. - La Maison du Grand-Coq</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000244.TIF)" n="lie.000017" type="image">245</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000018">I I - Le Théâtre de la Cité</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000288.TIF)" n="lie.000018" type="image">289</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000019">III. - Spectacles et plaisirs</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000313.TIF)" n="lie.000019" type="image">314</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000020">IV. - Les écrivains et le bien-manger</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000333.TIF)" n="lie.000020" type="image">334</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000021">V. - Une station balnéaire rue Saint-Lazare</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000341.TIF)" n="lie.000021" type="image">342</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000022">VI. - Les charitables musiciens de<placeName>Paris</placeName></seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000348.TIF)" n="lie.000022" type="image">349</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000023">VII- - La foire de<placeName>Bezons</placeName></seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000354.TIF)" n="lie.000023" type="image">355</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000024">VIII. - Sports parisiens</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000362.TIF)" n="lie.000024" type="image">363</xref>
</cell>
</row>
<row>
<cell>
<seg n="int.000025">IX. - Un succès de librairie</seg>
</cell>
<cell>
<xref from="FOREIGN (0165680/000373.TIF)" n="lie.000025" type="image">374</xref>
</cell>
</row>
</table>
</div1>
</div0>
</body>
</text>
</TEI.2>"""
