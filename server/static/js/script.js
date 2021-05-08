const modalImage = new bootstrap.Modal(document.querySelector("#modal-image"), {keyboard: false})
const modalVideo = new bootstrap.Modal(document.querySelector("#modal-video"), {keyboard: false})

document.querySelector("#btn-upload-image").onclick = async () => {
    const file = document.querySelector("#image-file")
    if (file.files.length == 0){
        toastr.error("You must select image first");
        return;
    }

    $.LoadingOverlay("show")
    imageSrc = document.querySelector(".src-image")
    imageSrc.src = URL.createObjectURL(file.files[0]);
    imageSrc.onload = function() {
      URL.revokeObjectURL(imageSrc.src) // free memory
    }
    
    
    const formData = new FormData();
    formData.append("file", file.files[0]);
    const res = await axios.post('/upload-image', formData, {
        headers: {
        'Content-Type': 'multipart/form-data'
        }
    })
    if (!res.data.success){
        $.LoadingOverlay("hide")
        toastr.error("Something was wroing with your server!")
        return;
    }
    document.querySelector(".result-image").src = res.data["image_url"]
    $.LoadingOverlay("hide")
    modalImage.show()
}

document.querySelector("#btn-stream-video").onclick = async () => {
    const url = document.querySelector("#video-url").value.trim()
    if (url.length == 0){
        toastr.error("You must type the url of video");
        return;
    }
    $.LoadingOverlay("show")
    
    const result = await axios.post('/update-stream', {url})
    if (!result.data.success){
        $.LoadingOverlay("hide")
        toastr.error("Something was wroing with your server!")
        return;
    }
    $.LoadingOverlay("hide")
    modalVideo.show()
    document.querySelector(".result-video").src = ""
    document.querySelector(".result-video").src = "/video-result"
    document.querySelector(".origin-video").src = ""
    document.querySelector(".origin-video").src = "/video-origin"
}