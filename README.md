# Cherrytree to Markdown (ct2md)
Convert Cherrytree documents to markdown for [Zettlr](https://www.zettlr.com/) or [logseq](https://logseq.com/).
Over the years, I have used Cherrytree for all my personal notes, and I have been very happy with it.
However, having the ability to convert those notes to markdown to use them in Zettlr or logseq is appealing, therefore this project.


## Usage

1. Execute cherrytree and then go to File -> Export -> Export to HTML
2. In the Export to HTML select include node names and links tree in every page, but do not select single file.
3. Execute ct2md.py

```
Usage:
  ct2md.py  [flags]

Flags:
   -c, --cherrytree <path> Executes cherrytree with <path> to a document to export to HTML
                           the document will be exported to the value in --path
                           **NOT WORKING**
   -C, --CherryTree <path> Same as --cherrytree, but executes it under flatpak
                           **NOT WORKING**
   -p, --path    <path>    Path to the cherrytree HTML export to be converted (default HTML)
                           If --cherrytree or --CherryTree is used then <path> is overwriten
                           with the output of the cherrytree export
   -o, --output  <path>    Output folder with the resulting markdown (default markdown)
   -h, --help              Prints this help
   -v, --verbose           Produces verbose stdout output
   -z, --zettlr            Produces Zettlr markdown
   -i, --id                Generates a Zettlr id using YYYYMMDDnnnn where nnnn is sequential
   -l, --logseq            Produces Logseq markdown
```
## Example

```
./ct2md.py -i -z -p notes.ctb_HTML -o notes
```

This will generate markdown in the _notes_ folder. The input comes from the folder notes.ctb_HTML.
The generated markdown use the extensions that Zettlr expects.

