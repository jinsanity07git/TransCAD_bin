import os
from ipywidgets import FileUpload
from IPython.display import display

# Create the file upload widget
binf = FileUpload(
    accept='.bin',  
    description='BIN file' ,
    multiple=False  # Allow multiple files to be uploaded
)

dcbf = FileUpload(
    accept='.dcb',  
    description='DCB file' ,
    multiple=False  # Allow multiple files to be uploaded
)

# Display the widget
fupload = (binf,dcbf)


def save_uploaded_file(uploader,indir):
    for name, file_info in uploader.value.items():
        print(f"Uploaded file name: {name}")
        print(f"File size: {file_info['metadata']['size']} bytes")
        furl = os.path.join(indir,name)
        with open(furl,"wb") as f:
            f.write(uploader.data[0])
        return furl
    
def fname_wot_ext(file_path):
    filename_with_extension = os.path.basename(file_path)
    filename_without_extension, _ = os.path.splitext(filename_with_extension)
    return filename_without_extension

def save_binbcb(fupload,indir):
    fs = []
    for uploader in fupload:
        furl = save_uploaded_file(uploader,indir)
        fs.append(furl)   
    if fname_wot_ext(fs[0]) != fname_wot_ext(fs[1]):
        raise BaseException("filename of the BIN and DCB file should be exactly the same!")
    return fs