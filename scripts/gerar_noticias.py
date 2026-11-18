import html
import io
import json
import os
import re
import unicodedata
from string import Template
from urllib.parse import unquote

from PIL import Image, ImageOps

SITE = 'https://borgessfut.com.br'  # se o endereço do site mudar, troque só esta linha
NOME = 'BORGESSFUT'
AUTOR = 'Por Felipe Borges'
MESES = ['jan.', 'fev.', 'mar.', 'abr.', 'mai.', 'jun.', 'jul.', 'ago.', 'set.', 'out.', 'nov.', 'dez.']
PAGINAS_FIXAS = ['', 'sobre.html', 'noticias.html', 'alem-do-futebol.html', 'projetos.html', 'portfolio.html', 'contato.html']


def e(s):
    return html.escape(s or '', quote=True)


def slug(t):
    t = unicodedata.normalize('NFD', (t or '').lower())
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r'[^a-z0-9]+', '-', t)
    return t.strip('-')


def data_longa(s):
    p = (s or '')[:10].split('-')
    if len(p) != 3:
        return ''
    try:
        return '%d de %s de %s' % (int(p[2]), MESES[int(p[1]) - 1], p[0])
    except Exception:
        return ''


def limpar_html(t):
    t = t.replace('&nbsp;', ' ').replace('\u00a0', ' ')
    t = re.sub(r'<script.*?</script>', '', t, flags=re.S | re.I)
    t = re.sub(r'\son\w+\s*=\s*("[^"]*"|\'[^\']*\')', '', t, flags=re.I)
    t = re.sub(r'javascript:', '', t, flags=re.I)
    return t


def texto_simples(h):
    h = re.sub(r'<[^>]+>', ' ', h)
    h = html.unescape(h).replace('\u00a0', ' ')
    return re.sub(r'\s+', ' ', h).strip()


def primeiro_paragrafo(texto):
    t = (texto or '').strip()
    if t.startswith('<'):
        for m in re.finditer(r'<p[^>]*>(.*?)</p>', t, flags=re.S | re.I):
            s = texto_simples(m.group(1))
            if s:
                return s
        return texto_simples(t)
    for bloco in re.split(r'\n\s*\n', t):
        s = re.sub(r'\s+', ' ', bloco).strip()
        if s:
            return s
    return ''


def resumir(s, limite=180):
    if len(s) <= limite:
        return s
    corte = s[:limite].rsplit(' ', 1)[0]
    return corte.rstrip(' ,;:.-') + '…'


def gerar_og(imagem, destino):
    """Cria uma versão leve (1200x630) da foto da notícia."""
    if not imagem or imagem.startswith(('http://', 'https://')):
        return False
    caminho = unquote(imagem).lstrip('/')
    if not os.path.isfile(caminho):
        return False
    try:
        im = Image.open(caminho)
        im = ImageOps.exif_transpose(im).convert('RGB')
        im = ImageOps.fit(im, (1200, 630), Image.LANCZOS, centering=(0.5, 0.4))
        buf = io.BytesIO()
        for q in (85, 78, 70, 60, 50):
            buf = io.BytesIO()
            im.save(buf, 'JPEG', quality=q, optimize=True, progressive=True)
            if buf.tell() <= 250 * 1024:
                break
        with open(destino, 'wb') as f:
            f.write(buf.getvalue())
        return True
    except Exception as erro:
        print('Aviso: não consegui preparar a imagem', imagem, erro)
        return False


PAGINA = Template('''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="/">
  <title>$titulo | $nome</title>
  <link rel="icon" href="logo-site.png">
  <link rel="canonical" href="$og_url">
  <meta name="description" content="$descricao">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="$nome">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:url" content="$og_url">
  <meta property="og:title" content="$titulo">
  <meta property="og:description" content="$descricao">
  <meta property="og:image" content="$og_img">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,600;0,700;1,700&family=Lato:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="estilo.css">
</head>
<body>
  <div id="cabecalho"></div>

  <main class="pagina larga" id="conteudo">
    <div class="artigo">
$corpo
    </div>
  </main>

  <div id="rodape"></div>
  <script src="site.js"></script>
  <script>
    document.querySelectorAll('nav a').forEach(function (a) {
      a.classList.toggle('ativo', a.getAttribute('href') === '$ativo');
    });
  </script>
</body>
</html>
''')


def montar(n, id_, descricao, tem_og):
    titulo = n.get('titulo') or ''
    outros = n.get('secao') == 'Outros esportes'
    volta = 'alem-do-futebol.html' if outros else 'noticias.html'
    volta_txt = '← Voltar a Além do futebol' if outros else '← Voltar às notícias'

    partes = ['      <a class="voltar" href="%s">%s</a>' % (volta, volta_txt)]
    if outros and n.get('esporte'):
        partes.append('      <div><span class="etiqueta">%s</span></div>' % e(n['esporte']))
    partes.append('      <h1>%s</h1>' % e(titulo))
    if n.get('subtitulo'):
        partes.append('      <p class="subtitulo-artigo">%s</p>' % e(n['subtitulo']))
    partes.append('      <p class="autor-artigo">%s</p>' % e(AUTOR))
    dl = data_longa(n.get('data'))
    if dl:
        partes.append('      <p class="data-artigo">%s</p>' % e(dl))
    if n.get('imagem'):
        partes.append('      <img src="%s" alt="%s">' % (e(n['imagem']), e(titulo)))

    texto = n.get('texto') or ''
    if texto.strip().startswith('<'):
        partes.append('      <div class="texto rico">%s</div>' % limpar_html(texto))
    else:
        partes.append('      <div class="texto">%s</div>' % e(texto))

    link = n.get('link') or ''
    if re.match(r'^https?://', link):
        partes.append('      <a class="botao" href="%s" target="_blank" rel="noopener">Ler na fonte original →</a>' % e(link))

    return PAGINA.safe_substitute(
        titulo=e(titulo),
        nome=NOME,
        descricao=e(descricao),
        og_url='%s/noticia/%s.html' % (SITE, id_),
        og_img=('%s/og/%s.jpg' % (SITE, id_)) if tem_og else ('%s/compartilhar.jpg' % SITE),
        corpo='\n'.join(partes),
        ativo=('alem-do-futebol.html' if outros else 'noticias.html'),
    )


def gerar_sitemap(urls):
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, lastmod in urls:
        extra = '<lastmod>%s</lastmod>' % lastmod if lastmod else ''
        linhas.append('  <url><loc>%s</loc>%s</url>' % (html.escape(loc), extra))
    linhas.append('</urlset>')
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write('\n'.join(linhas) + '\n')
    with open('robots.txt', 'w', encoding='utf-8') as f:
        f.write('User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE)


def main():
    with open('content/noticias.json', encoding='utf-8') as f:
        dados = json.load(f)

    os.makedirs('noticia', exist_ok=True)
    os.makedirs('og', exist_ok=True)

    urls = [('%s/%s' % (SITE, p), '') for p in PAGINAS_FIXAS]
    vistos = set()
    total = 0
    for n in dados.get('itens', []):
        id_ = '%s-%s' % (slug(n.get('titulo')), (n.get('data') or '')[:10])
        if id_ in vistos:
            continue
        vistos.add(id_)

        tem_og = gerar_og(n.get('imagem'), 'og/%s.jpg' % id_)
        descricao = resumir(primeiro_paragrafo(n.get('texto'))) or n.get('subtitulo') or 'Notícia do BORGESSFUT.'
        with open('noticia/%s.html' % id_, 'w', encoding='utf-8') as f:
            f.write(montar(n, id_, descricao, tem_og))

        data = (n.get('data') or '')[:10]
        urls.append(('%s/noticia/%s.html' % (SITE, id_), data if re.match(r'^\d{4}-\d{2}-\d{2}$', data) else ''))
        total += 1

    gerar_sitemap(urls)
    print('Páginas de notícias geradas:', total)


if __name__ == '__main__':
    main()
