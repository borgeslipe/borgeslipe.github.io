(function () {
  // ---------- App instalável (PWA) ----------
  function ligar(tag, atributos) {
    var e = document.createElement(tag);
    Object.keys(atributos).forEach(function (k) { e.setAttribute(k, atributos[k]); });
    document.head.appendChild(e);
  }
  if (!document.querySelector('link[rel="manifest"]')) ligar('link', { rel: 'manifest', href: '/manifest.json' });
  if (!document.querySelector('meta[name="theme-color"]')) ligar('meta', { name: 'theme-color', content: '#0181f3' });
  if (!document.querySelector('link[rel="apple-touch-icon"]')) ligar('link', { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' });
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/sw.js').catch(function () {});
    });
  }

  // Endereços das redes sociais: troque aqui se algum for diferente
  var redes = {
    instagram: 'https://www.instagram.com/borgessfut/',
    tiktok: 'https://www.tiktok.com/@borgessfut',
    x: 'https://x.com/borgessfut'
  };

  var nomes = { instagram: 'Instagram', tiktok: 'TikTok', x: 'X' };

  var icones = {
    instagram: '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="17.2" cy="6.8" r="1.2" fill="currentColor"/></svg>',
    tiktok: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/></svg>',
    x: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"/></svg>'
  };

  function botoesRedes() {
    return Object.keys(redes).map(function (k) {
      return '<a class="rede" href="' + redes[k] + '" target="_blank" rel="noopener" aria-label="' + nomes[k] + ' do BORGESSFUT">' + icones[k] + '</a>';
    }).join('');
  }

  // Abas do menu: [nome do arquivo sem .html, texto que aparece]
  var paginas = [
    ['sobre', 'Sobre'],
    ['noticias', 'Notícias'],
    ['alem-do-futebol', 'Além do futebol'],
    ['projetos', 'Projetos'],
    ['portfolio', 'Portfólio'],
    ['contato', 'Contato']
  ];
  var atual = (location.pathname.split('/').pop() || 'index').replace('.html', '');
  if (atual === 'projeto') atual = 'projetos';

  var links = paginas.map(function (p) {
    var ativo = (atual === p[0]) ? ' class="ativo"' : '';
    return '<a href="' + p[0] + '.html"' + ativo + '>' + p[1] + '</a>';
  }).join('');

  var cab = document.getElementById('cabecalho');
  if (cab) {
    cab.outerHTML =
      '<header>' +
        '<a href="index.html" class="marca">' +
          '<img src="logo-site.png" alt="Logo BORGESSFUT">' +
          '<span>BORGESSFUT</span>' +
        '</a>' +
        '<button type="button" class="menu-btn" id="menu-btn" aria-label="Abrir menu" aria-expanded="false">' +
          '<span></span><span></span><span></span>' +
        '</button>' +
        '<nav>' + links + '</nav>' +
      '</header>';

    // Abre e fecha o menu no celular
    var hdr = document.querySelector('header');
    var btn = document.getElementById('menu-btn');
    if (hdr && btn) {
      btn.addEventListener('click', function () {
        var aberto = hdr.classList.toggle('aberto');
        btn.setAttribute('aria-expanded', aberto ? 'true' : 'false');
        btn.setAttribute('aria-label', aberto ? 'Fechar menu' : 'Abrir menu');
      });
    }
  }

  var rod = document.getElementById('rodape');
  if (rod) {
    rod.outerHTML =
      '<footer>' +
        '<div class="redes">' + botoesRedes() + '</div>' +
        '<p>© BORGESSFUT</p>' +
      '</footer>';
  }

  // ---------- Botão "Instalar o app" no rodapé ----------
  var rodape = document.querySelector('footer');
  var instalado = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;
  if (rodape && !instalado) {
    var copia = rodape.querySelector('p');
    var pedido = null;

    var botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'btn-instalar';
    botao.hidden = true;
    botao.textContent = 'Instalar o app do BORGESSFUT';
    rodape.insertBefore(botao, copia);

    window.addEventListener('beforeinstallprompt', function (e) {
      e.preventDefault();
      pedido = e;
      botao.hidden = false;
    });
    botao.addEventListener('click', function () {
      if (!pedido) return;
      pedido.prompt();
      pedido.userChoice.then(function () { pedido = null; botao.hidden = true; });
    });
    window.addEventListener('appinstalled', function () { botao.hidden = true; });

    // iPhone e iPad não têm o botão automático
    if (/iphone|ipad|ipod/i.test(navigator.userAgent)) {
      var dica = document.createElement('p');
      dica.className = 'dica-instalar';
      dica.textContent = 'No iPhone: toque em Compartilhar e depois em "Adicionar à Tela de Início".';
      rodape.insertBefore(dica, copia);
    }
  }
})();
