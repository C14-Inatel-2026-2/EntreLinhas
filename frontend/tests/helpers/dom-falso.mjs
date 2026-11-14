export class NoFalso {
  constructor(tag = "div") {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.parentNode = null;
    this.attributes = {};
    this.dataset = {};
    this.disabled = false;
    this.hidden = false;
    this.className = "";
    this._texto = "";
    this._ouvintes = {};
    const nome = this;
    this.classList = {
      contains: (c) => nome.className.split(/\s+/).includes(c),
      toggle: (c, forcar) => {
        const tem = nome.className.split(/\s+/).includes(c);
        const ligar = forcar ?? !tem;
        const sem = nome.className.split(/\s+/).filter((x) => x && x !== c);
        nome.className = (ligar ? [...sem, c] : sem).join(" ");
        return ligar;
      }
    };
  }
  get textContent() { return this._texto + this.children.map((c) => c.textContent).join(""); }
  set textContent(v) { this._texto = String(v); this.children = []; }
  get isFragment() { return this.tagName === "#FRAGMENT"; }
  setAttribute(n, v) { this.attributes[n] = String(v); if (n === "type") this.type = String(v); }
  getAttribute(n) { return this.attributes[n] ?? null; }
  _adotar(filho) { filho.parentNode = this; this.children.push(filho); }
  append(...nos) {
    nos.forEach((no) => {
      if (typeof no === "string") { this._texto += no; return; }
      if (no.isFragment) { [...no.children].forEach((f) => this._adotar(f)); no.children = []; } else this._adotar(no);
    });
  }
  replaceChildren(...nos) { this.children = []; this._texto = ""; this.append(...nos); }
  contains(no) { return no === this || this.children.some((c) => c.contains(no)); }
  closest(seletor) { for (let n = this; n; n = n.parentNode) if (n.matches?.(seletor)) return n; return null; }
  matches(seletor) {
    const m = seletor.match(/^([a-z]+)?(?:\[([\w-]+)\])?((?:\.[\w-]+)*)(:not\(:disabled\))?$/);
    if (!m) throw new Error(`Seletor não suportado: ${seletor}`);
    const [, tag, attr, classes, naoDesab] = m;
    if (tag && this.tagName !== tag.toUpperCase()) return false;
    if (attr && !(attr in this.attributes) && !(attr.startsWith("data-") && this.dataset[attr.slice(5)] !== undefined)) return false;
    if (classes && !classes.split(".").filter(Boolean).every((c) => this.classList.contains(c))) return false;
    if (naoDesab && this.disabled) return false;
    return true;
  }
  querySelectorAll(seletor) {
    const achados = [];
    const percorrer = (no) => no.children.forEach((f) => { if (f.matches(seletor)) achados.push(f); percorrer(f); });
    percorrer(this);
    return achados;
  }
  querySelector(seletor) { return this.querySelectorAll(seletor)[0] ?? null; }
  addEventListener(tipo, fn) { (this._ouvintes[tipo] ||= []).push(fn); }
  disparar(tipo, evento) { (this._ouvintes[tipo] || []).forEach((fn) => fn(evento)); }
}

export function instalarDomFalso() {
  const registro = new Map();
  const doc = {
    createElement: (tag) => new NoFalso(tag),
    createDocumentFragment: () => new NoFalso("#fragment"),
    getElementById: (id) => registro.get(id) ?? null
  };
  globalThis.document = doc;
  ["tabuleiro", "confirmar-palpite", "selecao-palpite"].forEach((id) => registro.set(id, new NoFalso(id === "tabuleiro" ? "div" : "button")));
  return registro;
}