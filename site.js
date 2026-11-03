(function () {
  var paginas = [
    ['sobre', 'Sobre'],
    ['noticias', 'Notícias'],
    ['projetos', 'Projetos'],
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
          '<img src="logo,png.png" alt="Logo BORGESSFUT">' +
          '<span>BORGESSFUT</span>' +
        '</a>' +
        '<nav>' + links + '</nav>' +
      '</header>';
  }

  var rod = document.getElementById('rodape');
  if (rod) rod.outerHTML = '<footer>© BORGESSFUT</footer>';
})();
