#!/usr/bin/env python

"""make-supplementary-pdf.py: Generate Latex code for image comparison for supplementary.
Copyright (C) 2018  Orazio Gallo

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
import sys
import json
from PIL import Image

__maintainer__ = "Orazio Gallo"
__company__ = "NVIDIA Corp."
__email__ = "ogallo@nvidia.com"
__status__ = "Development"

# Standard packages to import
std_packages = ["amsmath", "color", "epsfig", "hyperref", "tikz", "float"]


# Little helper to localize typos in the JSON file
def open_and_check(json_filename):
    try:
        return json.load(open(json_filename))
    except ValueError as e:
        print('Something wrong with the json file.')
        print("Here's a hint: %s" % e)
        return None


# The file separator changes with the OS, but latex only wants "/"
def sep(line):
    return line.replace('\\', '/')


# Parse authors and insitutions
def create_authors(authors, institutions):
    authors_str = "\\author{"
    max_institution_id = 0

    # List of authors
    for a, author in enumerate(authors):
        if a > 0:
            authors_str += ", "
        authors_str += author["name"]
        authors_str += "$^{"
        for i in range(len(author["institution_id"])):
            if i > 0:
                authors_str += ", "
            authors_str += str(author["institution_id"][i])
            if author["institution_id"][i] > max_institution_id:
                max_institution_id = author["institution_id"][i]
        authors_str += "}$"
    authors_str += "\\\\\n"

    # Now the institutions
    add_institutions = True
    if len(institutions) != max_institution_id:
        print(">> Uhm, something's wrong, check that you listed all the institutions.")
        add_institutions = False
    if add_institutions:
        authors_str += "\small{"
        for i, institution in enumerate(institutions):
            if i > 0:
                authors_str += "\hspace{1.5em} "
            authors_str += "$^" + str(i + 1) + "$" + institution
        authors_str += "}"

    authors_str += "}\n\n"
    return authors_str


# Header of the tex file
def preamble(title, packages, links_color, instructions="", authors=""):
    pre = "% AUTO-GENERATED CODE, DO NOT MODIFY!!\n"
    pre += "\\documentclass[10pt,letterpaper]{article}\n"
    for package in packages:
        pre += "\\usepackage{"
        pre += package
        pre += "}\n"
    pre += "\n"
    pre += "\\addtolength{\\oddsidemargin}{-.875in}\n"
    pre += "\\addtolength{\\evensidemargin}{-.875in}\n"
    pre += "\\addtolength{\\textwidth}{1.75in}\n"
    pre += "\\addtolength{\\topmargin}{-.875in}\n"
    pre += "\\addtolength{\\textheight}{1.75in}\n"
    pre += "\n"
    pre += "\\newsavebox\\mybox\n"
    pre += "\n"
    pre += "\\definecolor{links_color}{RGB}{" + links_color + "}\n"
    pre += "\\hypersetup{colorlinks=true, linkcolor=links_color}\n\n"
    pre += "\\title{" + title + "\\\\ ---Supplementary Material---}\n\n"
    pre += "\\date{\\vspace{-5ex}}\n\n"
    pre += "\\newcommand\\blindfootnote[1]{\n"
    pre += "\\begingroup\n"
    pre += "\\renewcommand\\thefootnote{}\\footnote{#1}\n"
    pre += "\\addtocounter{footnote}{-1}\n"
    pre += "\\endgroup\n"
    pre += "}\n\n"
    pre += "\\begin{document}\n\n"
    pre += authors
    pre += "\\maketitle\n\n"
    pre += "\\vspace{10mm}\n"
    pre += "\\noindent "
    pre += instructions
    pre += "\\blindfootnote{Document created with code from: \href{https://github.com/gorazione/make_supplementary}{\color{black}https://github.com/gorazione/make\_supplementary}}\n\n"
    return pre


# Closing code for the tex file
def closure():
    post = "\\end{document}\n"
    return post


# Create the crops for the comparisons
def crop_images(img_names, crops):
    out_dir = os.path.dirname(img_names[0]) + os.sep + "crops"
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    crop_names = []
    for img_path in img_names:
        tmp_image = Image.open(img_path)
        ignore, img_name = os.path.split(img_path)
        img_name, ignore = os.path.splitext(img_name)
        crop_names_tmp = []
        for crop_id, crop in enumerate(crops):
            crop_filename = sep(out_dir + os.sep + img_name + "_crop_" + str(crop_id) + ".png")
            if not os.path.isfile(crop_filename):
                # PIL crop:  left, top, right, and bottom pixel
                result = tmp_image.crop((crop[0], crop[1], crop[2], crop[3]))
                result.save(crop_filename)
            crop_names_tmp.extend([crop_filename])
        crop_names.append(crop_names_tmp)
    return crop_names


def get_num_pixels(filepath):
    width, height = Image.open(filepath).size
    return width, height


# Create the hyperlinks to switch beween results and different comparisons
def create_links(comparison, comp_id, fig_id):
    tex = ""
    tmp = 0
    tex += "\\noindent\\newline\\vspace{3mm}\n"
    for lbl in comparison["labels"]:
        tex += "\\hyperlink{fig:" + str(fig_id + tmp) + "}{\\Large{" + lbl + "}}\\newline\\vspace{3mm}\n"
        tmp += 1
    tex += "\\\\\n"
    tex += "\\begin{center}\n"
    if comp_id == 0:
        # Making the text white and with no link to maintain the layout
        tex += "\\textcolor{white}{$\\leftarrow$ Previous Comparison}\\qquad\n"
    else:
        tex += "\\hyperlink{comparison:" + str(comp_id - 1) + "}{$\\leftarrow$ Previous Comparison}\\qquad\n"
    tex += "\\hyperlink{comparison:" + str(comp_id + 1) + "}{Next Comparison $\\rightarrow$}"
    tex += "\\end{center}\n"
    return tex


def add_comparison(comparison, comp_id, fig_id):

    tex = ""
    links = create_links(comparison, comp_id, fig_id)
    first_image = True
    fig_w = comparison["fig_width_relative"]
    crops_height = comparison["crops_height_in"]

    crops = comparison["crops"]
    if crops:
        pix_w, pix_h = get_num_pixels(comparison["inputs"][0])

    for image_id, image_name in enumerate(comparison["inputs"]):
        tex += "\\clearpage\n"

        if first_image:
            tex += "%%%%%%%%%%%%% New Comparison %%%%%%%%%%%%%\n"
            tex += "\\hypertarget{comparison:" + str(comp_id) + "}{}\n"
            first_image = False

        tex += "\\begin{figure*}[h!]\n"
        tex += "\\centering\n"

        if crops:
            # Generate the crops
            crops_path = crop_images(comparison["inputs"], crops)

            tex += "\\sbox\\mybox{\\includegraphics[width=" + str(fig_w) + "\\textwidth]{" + image_name + "}}\n"
            tex += "\\begin{tikzpicture}[x=\\wd\\mybox/" + str(pix_w) + ", y=\\ht\\mybox/" + str(pix_h) + "]\n"
            tex += "\\node[anchor=south west,inner sep=0pt] at (0,0) {\\usebox\\mybox};\n"
            for crop_id in range(len(crops)):
                # JSON file has: left, upper, right, and bottom
                # tikz: (left,bottom) rectangle (right,top);
                tex += "\\draw[blue, ultra thick, rounded corners] (" + str(crops[crop_id][0]) + "," + str(pix_h - crops[crop_id][3]) + ") rectangle (" + str(crops[crop_id][2]) + ", " + str(pix_h - crops[crop_id][1]) + ");\n"
            tex += "\\draw[black,thin] (0,0) rectangle + (" + str(pix_w) + "," + str(pix_h) + ");\n"
            tex += "\\end{tikzpicture}\\\\\n"
            tex += "\\vspace{1mm}\n"
            for crop_id in range(len(crops)):
                tex += "\\frame{\\includegraphics[height=" + str(crops_height) + "in]{" + crops_path[image_id][crop_id] + "}}\hfil\n"
        else:
            tex += "\\frame{\\includegraphics[width=" + str(fig_w) + "\\textwidth]{" + image_name + "}}\n"

        tex += "\\caption{" + comparison["caption"] + "}"
        tex += "\\hypertarget{fig:" + str(fig_id) + "}{}\n"
        fig_id += 1
        tex += "\\end{figure*}\n"
        tex += "\\begin{center}\n"
        tex += "\huge{" + comparison["labels"][image_id] + "}\n"
        tex += "\\end{center}\n"
        tex += links + "\n"
        tex += "\\clearpage\n\n"
    return tex, fig_id


def main():
    json_name = sys.argv[1]
    json_data = open_and_check(json_name)
    if not json_data:
        print('Terminating.')
        return

    packages = std_packages + json_data["packages"]
    title = json_data["title"]
    links_color = json_data["links_color"]
    instructions = json_data["instructions"]

    if json_data["anonymous"]:
        print(">> Omitting authors for anonymity, set 'anonymous' to 'false' if needed.")
        authors = ""
    else:
        print(">> Adding author information, set 'anonymous' to 'true' if you don't want me to.")
        authors = create_authors(json_data["authors"], json_data["institutions"])

    tex_source = preamble(title, packages, links_color, instructions, authors)

    comparisons = json_data["comparisons"]
    comp_id = 0
    fig_id = 0
    for comp in comparisons:
        tex, fig_id = add_comparison(comp, comp_id, fig_id)
        comp_id += 1
        tex_source += tex

    tex_source += closure()

    with open('supplementary.tex', 'w') as f:
        f.write(tex_source)


if __name__ == "__main__":
    main()
