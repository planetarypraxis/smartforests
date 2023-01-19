jQuery(function () {
  // Get the duration of an imported audio file
  let title, durationInput

  const observer = new MutationObserver(function (mutations_list) {

    mutations_list.forEach(() => {
      var upload = jQuery(document).find('section#upload-audio')[0]
      if (upload) {
        // Hide the title, for better UX
        title = jQuery(upload).find('input[name="media-chooser-upload-title"]').closest('li')
        durationInput = jQuery(upload).find('input[name="media-chooser-upload-duration"]').closest('li')
        title.hide()

        // Disable & hide the duration input
        durationInput.attr('disabled', true)
        durationInput.hide()

        observer.disconnect()
      }
    })

    jQuery('input[name="media-chooser-upload-file"]').on('change', async function (evt) {
      // Disable the submit button, just in case...
      const submit = jQuery('button[type="submit"]')
      submit.attr('disabled', true)

      // Get the file and duration
      const [file] = evt.target.files
      const ctx = new AudioContext()
      const buffer = await file.arrayBuffer()
      const data = await ctx.decodeAudioData(buffer)

      if (!!(data?.duration && !isNaN(data?.duration))) {
        const duration = Math.floor(data.duration)

        // Insert the duration into the input
        durationInput.show()
        jQuery('input[name="media-chooser-upload-duration"]').val(duration)

        // Show and autofill the title
        title.show()
        jQuery('input[name="media-chooser-upload-title"]').val(file.name)

      } else {
        jQuery(document).find('input[name="media-chooser-upload-file"]').val(null)
        alert("Something is wrong with that file, or it's the wrong file type. Supported formats are MP3, OGG or WAV")
      }

      // release the button
      submit.attr('disabled', false)
      observer.observe(document.querySelector('body'), { subtree: false, childList: true });
    });

  });

  observer.observe(document.querySelector('body'), { subtree: false, childList: true });
})
