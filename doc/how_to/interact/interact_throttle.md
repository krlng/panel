# Disable Continuous Updates with `Interact`

When interacting with functions which take a long time to run, realtime feedback can be a burden instead of being helpful. This guide addresses how to disable continuous updates with Panel `interact`.

Let's first create a simple function:


```{pyodide}
import panel as pn
pn.extension()

def f(x):
    return x
```

Now, let's call `interact` and set the argument `throttled` to `True`. The function will now only be run after the release of the mouse button (run the code cell to activate this callback).

```{pyodide}
pn.interact(f, x=10, throttled=True)
```

## Related Resources

- Read [Background > Widget Abbreviations for Panel Interact](../../background/interact/interact_abbreviations.md) for explanation.
- See [How-to > Autogenerate Widgets for Functions](../interact/index.md) for solutions.
- Consult [Reference > panel.interact] for technical details.
