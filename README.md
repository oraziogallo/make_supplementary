# "Supplementary" comparison generator

#### What is this code for? ####
This is a small Python utility to generate a PDF file that allows for easier comparisons between the images that are output by different algorithms. For instance, you can use this to compare different denoising methods on the same images. The idea is that the viewer can just flip between the results so that differences are easier to appreciate. The output is Latex code that can be compiled into PDF.

Take a look at [this example](https://drive.google.com/file/d/17Itta-z89lpWUdvUjpafKzJRSLoxHF5c/view) of a document auto-generated with this script.

While the script can be used and modified freely (MIT License), I ask that the link to this repository is not removed from the final PDF.

#### Requisites ####
* PILLOW/PIL for Python: https://python-pillow.org/
* Your favorite Latex package to compile the output into a PDF file.

#### How it works ####
You can run the code with:

```python make_supplementary.py suppl_json_template.json​```

The idea is that you should not have to modify neither the Latex, nor the Python code. Instead, use the JSON file to define your favorite parameters, list the images you want to include, and run the python code.

Add as many comparisons as needed, each of them defined by the following code in the JSON file: 
```css
{
    // Use the caption field to indicate to the viewer anything that they
    // should pay attention to in this particular comparison. It will be the
    // same caption for all the methods/images in this comparison.
    "caption": "This is the caption",

    // This is the size of the image relative to \textwidth
    "fig_width_relative" : 0.8,

    // The paths to the images for this comparison. Note that the number of
    // images can change for each comparison.
    "inputs": [
        "images/layer0.jpg",
        "images/layer1.jpg",
        "images/layer2.jpg"
    ],
    // These are the names of the different methods and their number must
    // match the number of images.
    "labels" : [
        "BM3D",
        "Gaussian Denoiser",
        "My method"
    ],
    // For each comparison, you can define any number of "crops," which are
    // regions that will be marked in the image and shown below. 
    // If you do not want to add crops, just leave the field empty.
    "crops" : [
        [Left, Top, Right, Bottom],
        [640, 128, 768, 384] // All numbers are in pixels
    ]
    // Height of the crops in inches
    "crops_height_in" : 1, 
}
```

For the rest of the parameters, the template JSON file in this repository should be self-explanatory.

##### Notes #####
* Depending on the aspect ratio and size of the image and the crops, you may have to play with `fig_width_relative` and/or `crops_height_in`. For the trick to work, each image must be in the exact same position in each page, which means that each image together with the cropped insets, the caption, and the links to other methods, all need to fit in one page.
* To switch between showing or hiding the authors, use the field ```"anonymous"``` in the JSON file. This can come in handy for anonymous submissions.
* The JSON parser is very sensitive to delimiters (or lack thereof). In case of errors parsing the JSON file, the code spits out a hint about the error and where it was found: look for missing or extra delimiters in lines preceding the line it indicates.
 

