import * as p from "@bokehjs/core/properties"
import {Markup} from "@bokehjs/models/widgets/markup"
import {ModelEvent} from "@bokehjs/core/bokeh_events"
import {PanelMarkupView} from "./layout"
import {serializeEvent} from "./event-to-object";
import {Attrs} from "@bokehjs/core/types"

export class DOMEvent extends ModelEvent {
  event_name: string = "dom_event"

  constructor(readonly node: string, readonly data: any) {
    super()
  }

  protected get event_values(): Attrs {
    return {model: this.origin, node: this.node, data: this.data}
  }
}

export function htmlDecode(input: string): string | null {
  var doc = new DOMParser().parseFromString(input, "text/html");
  return doc.documentElement.textContent;
}

export function runScripts(node: any): void {
  Array.from(node.querySelectorAll("script")).forEach((oldScript: any) => {
    const newScript = document.createElement("script");
    Array.from(oldScript.attributes)
      .forEach((attr: any) => newScript.setAttribute(attr.name, attr.value) );
    newScript.appendChild(document.createTextNode(oldScript.innerHTML));
    if (oldScript.parentNode)
      oldScript.parentNode.replaceChild(newScript, oldScript);
  });
}

export class HTMLView extends PanelMarkupView {
  model: HTML
  _event_listeners: any = {}

  connect_signals(): void {
    super.connect_signals()
    this.connect(this.model.properties.events.change, () => {
      this._remove_event_listeners()
      this._setup_event_listeners()
    })
  }

  protected rerender() {
    this.render()
    this.invalidate_layout()
  }

  render(): void {
    super.render()
    const html = this.process_tex()
    if (!html) {
      this.markup_el.innerHTML = '';
      return;
    }
    this.markup_el.innerHTML = html
    runScripts(this.markup_el)
    this._setup_event_listeners()
  }

  process_tex(): string {
    const decoded = htmlDecode(this.model.text);
    const text = decoded || this.model.text
    if (this.model.disable_math || !this.contains_tex(text))
      return text

    const tex_parts = this.provider.MathJax.find_tex(text)
    const processed_text: string[] = []

    let last_index: number | undefined = 0
    for (const part of tex_parts) {
      processed_text.push(text.slice(last_index, part.start.n))
      processed_text.push(this.provider.MathJax.tex2svg(part.math, {display: part.display}).outerHTML)

      last_index = part.end.n
    }

    if (last_index! < text.length)
      processed_text.push(text.slice(last_index))

    return processed_text.join("")
  }

  private contains_tex(html: string): boolean {
    if (!this.provider.MathJax)
      return false

    return this.provider.MathJax.find_tex(html).length > 0
  };

  private _remove_event_listeners(): void {
    for (const node in this._event_listeners) {
      const el: any = document.getElementById(node)
      if (el == null) {
        console.warn(`DOM node '${node}' could not be found. Cannot subscribe to DOM events.`)
        continue
      }
      for (const event_name in this._event_listeners[node]) {
	const event_callback = this._event_listeners[node][event_name]
	el.removeEventListener(event_name, event_callback)
      }
    }
    this._event_listeners = {}
  }

  private _setup_event_listeners(): void {
    for (const node in this.model.events) {
      const el: any = document.getElementById(node)
      if (el == null) {
        console.warn(`DOM node '${node}' could not be found. Cannot subscribe to DOM events.`)
        continue
      }
      for (const event_name of this.model.events[node]) {
	const callback = (event: any) => {
          this.model.trigger_event(new DOMEvent(node, serializeEvent(event)))
	}
        el.addEventListener(event_name, callback)
	if (!(node in this._event_listeners))
	  this._event_listeners[node] = {}
	this._event_listeners[node][event_name] = callback
      }
    }
  }
}

export namespace HTML {
  export type Attrs = p.AttrsOf<Props>

  export type Props = Markup.Props & {
    events: p.Property<any>
  }
}

export interface HTML extends HTML.Attrs {}

export class HTML extends Markup {
  properties: HTML.Props

  constructor(attrs?: Partial<HTML.Attrs>) {
    super(attrs)
  }

  static __module__ = "panel.models.markup"

  static {
    this.prototype.default_view = HTMLView
    this.define<HTML.Props>(({Any}) => ({
      events: [ Any, {} ]
    }))
  }
}
