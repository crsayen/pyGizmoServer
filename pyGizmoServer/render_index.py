from yattag import Doc

def render_index(started, version):
    with open('pyGizmoServer/styles.css') as f:
        css = f.read().replace('\n', '')
    doc, tag, text = Doc().tagtext()

    doc.asis('<!DOCTYPE html>')
    with tag('html'):
        with tag('head'):
            with tag('style'):
                text(css)
        with tag('body'):
            with tag('h1'):
                text('PyGizmoServer')
            with tag('h3'):
                text('Version: ')
                with tag('strong'):
                    text(f'{version}')
            with tag('h4'):
                text('Server sterted at: ')
                with tag('strong'): 
                    text(f'{started}')
            
    return doc.getvalue()
            