"""
<style>
    .bild {
        width: 100%;
        height: auto;
    }
</style>
<img alt="..." src="..." class="bild"/>
"""
import markdown

markdown.markdownFromFile(input='README.md', output='README.html')