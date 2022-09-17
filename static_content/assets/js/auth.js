const container = document.getElementById('auth_container_id');
const login_url = 'account/auth/login/'
const register_url = 'account/auth/register/'
console.log(window.location.pathname.includes(login_url))
console.log(window.location.pathname.includes(register_url))
if (window.location.pathname.includes(login_url)){
	container.classList.remove("right-panel-active");
}
else if(window.location.pathname.includes(register_url)){
	container.classList.add("right-panel-active");
}
