# Toolchain da versão JCSS

As fontes editoriais ficam em
`studies/ic-2026-2027/publications/jcss-journal/`. `build.py` compila o artigo e
o Online Resource 1 numa cópia temporária e executa `check.py`. `package.py`
prepara um kit de submissão a partir de um build completo e compara o texto
do PDF recompilado com o build. Nenhum comando envia arquivos à revista.

Instale Python 3.12, Tectonic e Poppler (`pdftotext` e `pdfinfo`). O ambiente
original usava Tectonic 0.17.0; use essa versão quando a comparação com o build
histórico exigir o mesmo engine. A
[instalação oficial do Tectonic](https://tectonic-typesetting.github.io/book/latest/getting-started/install.html)
descreve as distribuições disponíveis.

Baixe o template de artigo no
[canal oficial Springer Nature](https://www.springernature.com/gp/authors/campaigns/latex-author-support/see-where-our-services-will-take-you/18782940)
e extraia `sn-jnl.cls` e `sn-mathphys-num.bst` para uma pasta externa ao Git.
Preserve a versão e o SHA-256 obtidos. O template não foi copiado nem
relicenciado por esta extração. O empacotador aplica ao `.bst` a transformação
editorial já existente no estudo, durante o staging.

```sh
cd studies/ic-2026-2027/publications/jcss-journal
python3 build.py --template /path/to/springer-template \
  --tectonic /path/to/tectonic --cache /path/to/tectonic-cache \
  --out /path/to/scratch-build
python3 package.py --template /path/to/springer-template \
  --tectonic /path/to/tectonic --cache /path/to/tectonic-cache \
  --build /path/to/scratch-build --out /path/to/new-submission-kit
```

Os mesmos valores podem vir de `IC_STUDY_SPRINGER_TEMPLATE`,
`IC_STUDY_TECTONIC` e `IC_STUDY_TECTONIC_CACHE`; opções explícitas prevalecem.
`TECTONIC_CACHE_DIR` também é aceito para o cache. Sem configuração, o engine
vem do `PATH`, o template de `$XDG_DATA_HOME/ic-study/springer-template` e o
cache de `$XDG_CACHE_HOME/ic-study/tectonic`, com os padrões XDG usuais.
Para compatibilidade com o ambiente original, as pastas de template/cache
existentes em `.local/state/research-workbench/` e o engine Nix original são
fallbacks locais. Não são necessários em outro computador.

Os dois comandos usam `--only-cached` por padrão. Num computador novo, execute
`build.py` uma vez com `--allow-downloads` para preparar o cache escolhido;
depois execute sem essa opção. O
[manual do Tectonic](https://tectonic-typesetting.github.io/book/latest/getting-started/first-document.html)
explica o download inicial e a variável do cache. Preparar o cache é uma etapa
de dependências editoriais, não um experimento científico.

`build.py --submission` ativa os bloqueios editoriais adicionais já existentes.
Uma compilação normal bem-sucedida ainda pode conter declarações pendentes.
Builds e kits ficam fora das fontes; a pasta de build é substituída a cada
execução e a pasta do kit deve ser nova. Não faça commit de templates externos,
caches, PDFs de scratch ou dados privados.
