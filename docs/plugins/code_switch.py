import re
from markdown_it import MarkdownIt
from markdown_it.rules_block import StateBlock
from markdown_it.common import isSpace
from markdown_it.token import Token

def code_switch_plugin(md: MarkdownIt):
    """Plugin to handle code switches in markdown"""
    
    def code_switch_block(state: StateBlock, start_line: int, end_line: int, silent: bool):
        # Check if we're at the start of a code switch block
        pos = state.bMarks[start_line] + state.tShift[start_line]
        maximum = state.eMarks[start_line]
        
        # Must start with :::code-switch
        marker_str = state.src[pos:maximum]
        if not marker_str.startswith(':::code-switch'):
            return False
        
        # Extract the name attribute
        match = re.match(r':::code-switch\{name="([^"]+)"\}', marker_str.strip())
        if not match:
            return False
        
        switch_name = match.group(1)
        
        if silent:
            return True
        
        # Find the end of the code switch block
        next_line = start_line + 1
        auto_closed = False
        
        # Look for closing :::
        while next_line < end_line:
            pos = state.bMarks[next_line] + state.tShift[next_line]
            maximum = state.eMarks[next_line]
            line_text = state.src[pos:maximum].strip()
            
            if line_text == ':::':
                auto_closed = True
                break
            next_line += 1
        
        if not auto_closed:
            return False
        
        # Parse the code blocks inside
        content_lines = []
        for line_num in range(start_line + 1, next_line):
            pos = state.bMarks[line_num] + state.tShift[line_num]
            maximum = state.eMarks[line_num]
            content_lines.append(state.src[pos:maximum])
        
        content = '\n'.join(content_lines)
        tabs = parse_code_blocks(content)
        
        # Create tokens
        token_open = Token('code_switch_open', 'div', 1)
        token_open.info = switch_name
        token_open.map = [start_line, next_line + 1]
        token_open.markup = ':::code-switch'
        token_open.meta = {'tabs': tabs}
        
        token_close = Token('code_switch_close', 'div', -1)
        token_close.markup = ':::'
        
        state.push_token(token_open)
        state.push_token(token_close)
        
        state.line = next_line + 1
        return True
    
    def parse_code_blocks(content: str):
        """Parse code blocks from the content"""
        tabs = []
        
        # Split by code block markers
        blocks = re.split(r'\n```(\w+(?:-\w+)?)\s*([^\n]*)\n', content)
        
        i = 1
        while i < len(blocks):
            if i + 2 >= len(blocks):
                break
                
            language_id = blocks[i]
            label = blocks[i + 1].strip()
            code_content = blocks[i + 2].split('\n```')[0]
            
            # Extract language from the id (e.g., java-limelight -> java)
            language = language_id.split('-')[0]
            
            tabs.append({
                'id': language_id,
                'label': label or language_id,
                'language': language,
                'code': code_content.strip()
            })
            
            i += 3
        
        return tabs
    
    def render_code_switch(self, tokens, idx, options, env, renderer):
        """Render the code switch HTML"""
        token = tokens[idx]
        
        if token.nesting == 1:  # opening tag
            switch_name = token.info
            tabs = token.meta['tabs']
            
            html_parts = []
            
            # Generate tabs navigation
            html_parts.append(f'<div class="code-switch">')
            html_parts.append(f'<ul class="nav nav-tabs" id="{switch_name}-tablist" role="tablist">')
            
            for i, tab in enumerate(tabs):
                active_class = ' active' if i == 0 else ''
                selected = 'true' if i == 0 else 'false'
                
                html_parts.append(f'''
                <li class="nav-item" role="presentation">
                    <button
                        class="nav-link{active_class}"
                        id="{tab['id']}-tab"
                        data-bs-toggle="tab"
                        data-bs-target="#{tab['id']}-pane"
                        type="button"
                        role="tab"
                        aria-controls="{tab['id']}-pane"
                        aria-selected="{selected}"
                    >
                        {tab['label']}
                    </button>
                </li>''')
            
            html_parts.append('</ul>')
            
            # Generate tab content
            html_parts.append('<div class="code-switch-content tab-content">')
            
            for i, tab in enumerate(tabs):
                active_class = ' show active' if i == 0 else ''
                
                # Escape HTML in code
                escaped_code = (tab['code']
                               .replace('&', '&amp;')
                               .replace('<', '&lt;')
                               .replace('>', '&gt;'))
                
                html_parts.append(f'''
                <div
                    class="tab-pane{active_class}"
                    id="{tab['id']}-pane"
                    role="tabpanel"
                    aria-labelledby="{tab['id']}-tab"
                    tabindex="0"
                >
                    <pre><code class="language-{tab['language']}">{escaped_code}</code></pre>
                </div>''')
            
            html_parts.append('</div>')  # Close tab-content
            
            return ''.join(html_parts)
        else:  # closing tag
            return '</div>'  # Close code-switch
    
    # Register the block rule
    md.block.ruler.before(
        'fence',
        'code_switch',
        code_switch_block,
        {
            'alt': ['paragraph', 'reference', 'blockquote', 'fence']
        }
    )
    
    # Register the renderer
    md.renderer.rules['code_switch_open'] = render_code_switch
    md.renderer.rules['code_switch_close'] = render_code_switch
