import '../styles/index.scss';

import {times} from 'lodash';
import {LuminousGallery} from 'luminous-lightbox';

function toggle_loading(visible: boolean) {
  const loader = <HTMLElement>document.getElementsByClassName('loader')[0];
  if (visible) {
    loader.style.visibility = 'visible';
  } else {
    loader.style.visibility = 'hidden';
  }
}

function createGallery(images) {
  const gallery =
      <HTMLUListElement>(document.getElementsByClassName('gallery-root')[0]);
  toggle_loading(false);
  images.forEach(ele => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    const img = document.createElement('img');
    img.src = `thumbnails/${ele}`;
    a.href = `images/${ele}`;
    a.className = 'gallery';
    a.appendChild(img);
    li.appendChild(a);
    gallery.appendChild(li);
  });
  new LuminousGallery(document.getElementsByClassName('gallery'));
}
function invoke_query(e) {
  if (e.key === 'Enter') {
    query();
  }
}
function query() {
  const gallery = document.getElementsByClassName('gallery-root')[0];
  const prompt =
      (<HTMLInputElement>document.getElementsByName('search')[0]).value;
  while (gallery.firstChild) gallery.removeChild(gallery.firstChild);
  toggle_loading(true);
  fetch(`q/${escape(prompt)}`)
      .then(
          res => res.json().then(data => createGallery(data)),
      );
}

const imglist = [...Array(60)].map((v, i) => i * 18 + 1800);

console.log(imglist);
createGallery(imglist);
