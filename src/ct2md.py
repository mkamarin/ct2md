#!/usr/bin/env python3
# Convert Cherrytree documents to markdown for Zettlr or logseq

import os
import sys
import getopt
import inspect
import datetime
import subprocess
from markdownify import markdownify as mdConvert

verbose = False
mdType  = ""
zettlrID = False
mydate = datetime.datetime.now()
myID = datetime.datetime.now().strftime("%G%m%d")
myIDcount = 0

def vbprint(*args, **kwargs):
    if verbose:
        print(*args, **kwargs)


def error(*args, **kwargs):
    if verbose:
        print("ERROR [",os.path.basename(sys.argv[0]),":",
                inspect.currentframe().f_back.f_lineno,"]: ",
                *args, **kwargs, sep="", file = sys.stderr)
    else:
        print("ERROR: ", *args, **kwargs, sep="", file = sys.stderr)


def warn(*args, **kwargs):
    if verbose:
        print("WARNING [",os.path.basename(sys.argv[0]),":",
                inspect.currentframe().f_back.f_lineno,"]: ",
                *args, **kwargs, sep="", file = sys.stderr)
    else:
        print("WARNING: ", *args, **kwargs, sep="", file = sys.stderr)

def convert_file(src, dst, tags):
    """Convert the src HTML file to the dst markdown file

    Parameters
    ----------
    src : str
        Source full file HTML name
    dst : str
        Destination full file markdown name

    Returns
    -------
    Nothing
    """

    global myIDcount
    vbprint("CONVERT:",src,"->",dst, tags)
    try:
        dstFolder = os.path.dirname(dst)
        if not os.path.exists(dstFolder):
            os.makedirs(dstFolder)

        flSrc = open(src, 'r')
        html = flSrc.read()
        flSrc.close()
        md = mdConvert(html, heading_style="ATX", autolinks=False)

        # Front matter
        fm = ""
        tagx = [] # Contain the tags with blanks replaced by '-'
        for t in tags:
            if " " in t:
                tagx.append(t) # Let add the spaces too, as I don't know how zettlr handle tags with blanks
            tagx.append(t.replace(" ","-"))
        if mdType == "z":
            fm += "---\ntitle: " + tags[-1] + "\nkeywords:\n"
            for t in tagx:
                fm += "  - " + t + "\n"
            fm += "date: " + str(mydate) + "\n"
            if zettlrID:
                myIDcount += 1
                fm += "ID: " + myID + str(myIDcount).zfill(4) + "\n"
            fm += "---\n"
            fm += "\n# " + " / ".join(tags) + "\n  tags: #" + " #".join(tagx) + "\n"

        flDst = open(dst, 'w')
        flDst.write(fm)
        flDst.write(md)
        flDst.close()

    except OSError as e:
        error(e, " while converting files", src,"=>",dst)


def clone_file(src, dst):
    """Copy the src file to the dst file treating them as binary files

    Parameters
    ----------
    src : str
        Source full file name
    dst : str
        Destination full file name

    Returns
    -------
    Nothing
    """

    vbprint("CLONE:",src,"->",dst)
    try:
        dstFolder = os.path.dirname(dst)
        if not os.path.exists(dstFolder):
            os.makedirs(dstFolder)

        with open(src, 'rb') as flSrc:
            with open(dst, 'wb') as flDst:
                flDst.write(flSrc.read(4096))

    except OSError as e:
        error(e, " while clonning files", src,"=>",dst)

def traverse_path(arPath, arOutput):
 
    # Get a list of all files in the path
    for rootDir, subdirs, filenames in os.walk(arPath):
        try:
            for filename in filenames:
                vbprint("SOURCE: rootDir='",rootDir,"', subDirs=",
                        subdirs,", filename='",filename,"'", sep="")

                ## A) Prepare to process the file
                # sourceName is the complete file name including the directory structure (full path)
                sourceName = os.path.join(rootDir, filename)

                # name is the file name without path or extension
                # ext is the file extension
                name, ext = os.path.splitext(filename)
                print("NAME:",name,"EXT",ext)
                # base is the top sub-directory
                base = os.path.basename(rootDir)

                # root is the original path without the path directory arPath
                root = rootDir.replace(arPath + os.sep,"",1)
                root = '' if root == rootDir else root

                ## B) Process HTML files
                if ext in [".html", ".HTML"]:
                    targetName = name + ".md"
                    tags = name.replace("_"," ").split("--")
                    convert_file(sourceName,os.path.join(arOutput,root,targetName.replace("--",os.sep)),tags)
                else:
                    clone_file(sourceName,os.path.join(arOutput,root,filename))

        except OSError as e:
            error(e," while processing file", filename)

def export_cherrytree(arFlatpak, arInput, arPath):
    vbprint("Currently at", os.getcwd())
    print("Exporting cherrytree document: ",arInput," to ",arPath)
    ct = ['flatpak run com.giuspen.cherrytree' if arFlatpak else 'cherrytree', '-x', arPath, '-w', arInput]
    vbprint("Executing:"," ".join(ct))
    try:
        dstPath = os.path.dirname(arPath)
        if not os.path.exists(dstPath):
            os.makedirs(dstPath)
        res = subprocess.run(ct)
        if res.returncode != 0:
            error("Cherrytree execution failed with", res.returncode)
            sys.exit(2)
    except OSError as e:
        error(e," while executing cherrytree")
        sys.exit(2)

def arguments() :
    print("Usage:\n ",os.path.basename(sys.argv[0])," [flags]\n\nFlags:")
    print("   -c, --cherrytree <path> Executes cherrytree with <path> to a document to export to HTML")
    print("                           the document will be exported to the value in --path")
    print("   -C, --CherryTree <path> Same as --cherrytree, but executes it under flatpak")
    print("   -p, --path    <path>    Path to the cherrytree HTML export to be converted (default HTML)")
    print("                           If --cherrytree or --CherryTree is used then <path> is overwriten")
    print("                           with the output of the cherrytree export")
    print("   -o, --output  <path>    Output folder with the resulting markdown (default markdown)")
    print("   -h, --help              Prints this help")
    print("   -v, --verbose           Produces verbose stdout output")
    print("   -z, --zettlr            Produces Zettlr markdown")
    print("   -i, --id                Generates a Zettlr id using YYYYMMDDnnnn where nnnn is sequential")
    print("   -l, --logseq            Produces Logseq markdown")
    sys.exit(2)

def main(argv):
   # arguments:
   arPath       = "HTML"
   arOutput     = "markdown"
   arInput      = ""
   arFlatpak    = False
   arCherrytree = False

   try:
       opts, args = getopt.getopt(argv,"hvzlio:p:c:C:",
               ["help","verbose","zettlr","logseq","id","output=","path=","cherrytree","CherryTree"])
   except getopt.GetoptError as e:
      error(e)
      arguments()

   global mdType
   global verbose
   global zettlrID
   for opt, arg in opts:
      if (opt in ("-h","--help")) or (len(sys.argv) == 1):
         arguments()
      elif opt in ("-z", "--zettlr"):
          mdType = "z"
      elif opt in ("-l", "--logseq"):
          mdType = "l"
      elif opt in ("-i", "--id"):
          zettlrID = True
      elif opt in ("-v", "--verbose"):
          verbose = True
      elif opt in ("-o", "--output"):
         arOutput = arg
      elif opt in ("-p", "--path"):
         arPath = arg
      elif opt in ("-c", "--cherrytree"):
          arInput = arg
          arFlatpak = False
          arCherrytree = True
      elif opt in ("-C", "--CherryTree"):
          arInput = arg
          arFlatpak = True
          arCherrytree = True
      elif opt == "": 
          error("Invalid argument")
          arguments()

   if arCherrytree:
         export_cherrytree(arFlatpak, arInput, arPath)

   print("Converting folder: ",arPath," to ",arOutput)
   traverse_path(arPath, arOutput)
   print("done")

if __name__ == "__main__":
   main(sys.argv[1:])
