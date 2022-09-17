function displayLoadingSpinner(isDisplayed){
		let spinner_overlay = document.getElementById("id_loading_spinner")
        let spinner = document.querySelector('#spinner_id')
		if(isDisplayed){
			spinner_overlay.classList.add('show')
			spinner.classList.add('show')
		}
		else{
            spinner_overlay.classList.remove('show')
            spinner.classList.remove('show')
		}
	}