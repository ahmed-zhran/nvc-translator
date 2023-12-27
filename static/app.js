var translate = document.querySelector("#btn-translate");
var input_translate = document.querySelector("#input-translate")
var output_translate = document.querySelector("#output-translate")
var output_observations = document.querySelector("#output-giraffe-observations")
var output_feelings = document.querySelector("#output-giraffe-feelings")
var output_needs = document.querySelector("#output-giraffe-needs")
var output_requests = document.querySelector("#output-giraffe-requests")
var loading = document.querySelector("#loading");

// mock server
// var url = "https://lessonfourapi.tanaypratap.repl.co/translate/yoda.json"

function getText(text) {
  return text?.join(', ') || '';
}

// actual server
var url = "translate"

function urlfunc(url) {
  return url + "?" + "text=" + input_translate.value
}
function jsonEncoder(str) {
  try {
    let ans = JSON.parse(str);
    return ans;
  } catch (e) {
    console.log("e: ", e)
    return JSON.parse(JSON.parse(JSON.stringify(str)));
  }
}

function callback() {
  // Show spinner
  loading.style.display = 'block';
  // Hide translate button
  translate.style.display = 'none';

  fetch(urlfunc(url), {
    method: 'GET',
    mode: 'cors',
  })
    .then(response => response.json())
    .then(json => {
      let output_text = JSON.parse(json[0].translation);
      console.log("original res: ", json)
      console.log("json0: ", output_text)
      //********************* removing new lines and spaces *******************************************/
      // output_text = json[0].translation.split('\n').filter(s => Boolean(s.trim()));
      // console.log("json1: ", output_text)
      //********************* converting to array of objects (key: [values]) **************************/
      // output_text = output_text.map(e => ( { [`${e.split(':')[0]}`] : jsonEncoder(e.split(':')[1]) } ))
      // console.log("json2: ", output_text)
      //********************* reducing array of objects to one object *********************************/
      // output_text = output_text.reduce((prev, nxt) => ({...prev, ...nxt}), {})
      // console.log("json3: ", output_text)
      /*
        output_text: {
          "original_txt": "",
          "rephrased_txt": "",
          "observations": [],
          "feelings": [],
          "needs": [],
          "requests": []
        }
      */
      //********assigning values */
      output_translate.innerText = output_text.rephrased_txt; // For some reason the response comes back with leading \n's
      output_observations.innerText = getText(output_text.observations);
      output_feelings.innerText = getText(output_text.feelings);
      output_needs.innerText = getText(output_text.needs);
      output_requests.innerText = getText(output_text.requests);
      // Hide spinner
      loading.style.display = 'none';
      // Show translate button
      translate.style.display = 'block';
    }).catch(function errorhandler(error) {
      console.log("err: ", error)
      // Hide spinner
      loading.style.display = 'none';
      // Show translate button
      translate.style.display = 'block';

      alert("Something wrong with the server. Please try again later.")
    })
}

translate.addEventListener("click", callback)


// Setting icon according to theme
if (currentTheme === "dark") {
  document.querySelectorAll('.theme-icon').forEach((icon) => icon.innerHTML = `<i class="fas fa-sun" id="zon"></i>`)
} else {
  document.querySelectorAll('.theme-icon').forEach((icon) => icon.innerHTML = `<i class="fas fa-moon" id="maan"></i>`)
}
function changeTheme() {
  const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', theme);
  // Save the user's preference to local storage
  localStorage.setItem('theme', theme);

  // updating theme icon 
  if (theme === "light") {
    document.querySelectorAll('.theme-icon').forEach((icon) => icon.innerHTML = `<i class="fas fa-moon" id="maan"></i>`)
  } else {
    document.querySelectorAll('.theme-icon').forEach((icon) => icon.innerHTML = `<i class="fas fa-sun" id="zon"></i>`)
  }
}

// Navbar
window.addEventListener('scroll', () => {
  if (window.scrollY > 80) {
    document.querySelectorAll('.nav-wrapper').forEach((nav) => { nav.classList.add('active') })
  } else {
    document.querySelectorAll('.nav-wrapper').forEach((nav) => { nav.classList.remove('active') })
  }
})

function handleNavMenu() {
  // console.log(navbars);
  document.querySelectorAll('.navigation').forEach((navbar) => { navbar.classList.toggle('active') })
  document.querySelectorAll('.menu-icon').forEach((icon) => { icon.classList.toggle('active') })
}

// Scroll to translate section
function scrollToTranslator() {
  document.getElementById('translate-section').scrollIntoView({ behavior: 'smooth' });
}

function handleTranslateButton() {
  scrollToTranslator();
  localStorage.setItem('scrolled', 'true');
}

// Check localStorage on page load
window.onload = function () {
  if (localStorage.getItem('scrolled') === 'true') {
    scrollToTranslator();
  }
}