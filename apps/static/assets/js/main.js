const inputs = document.querySelectorAll(".input");

// Add focus class if input already has a value
inputs.forEach(input => {
	if (input.value !== "") {
		let parent = input.parentNode.parentNode;
		parent.classList.add("focus");
	}

	input.addEventListener("focus", addcl);
	input.addEventListener("blur", remcl);
});

function addcl(){
	let parent = this.parentNode.parentNode;
	parent.classList.add("focus");
}

function remcl(){
	let parent = this.parentNode.parentNode;
	if(this.value == ""){
		parent.classList.remove("focus");
	}
}