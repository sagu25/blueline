// user-profile.Component.ts   (violation: filename casing wrong, should be kebab-case)
// This file contains multiple Angular/TypeScript violations for demo purposes

import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { interval } from 'rxjs';

@Component({
  selector: 'app-user-profile',
  template: `
    <div [innerHTML]="userBio"></div>  <!-- violation: XSS risk, no DomSanitizer -->
    <div>{{ userData }}</div>
  `
  // violation: no changeDetection: ChangeDetectionStrategy.OnPush
})
export class UserProfileComponent implements OnInit {

  userData: any;        // violation: 'any' type
  userBio: any;         // violation: 'any' type
  private subscription: any;   // violation: 'any' type, also never unsubscribed

  constructor(private http: HttpClient) {}

  ngOnInit() {
    // violation: Observable never unsubscribed — memory leak
    this.subscription = interval(5000).subscribe(() => {
      this.loadUser();
    });
  }

  loadUser() {
    // violation: no type on response
    this.http.get('https://api.example.com/user/1').subscribe((data: any) => {
      this.userData = data;

      // violation: direct DOM manipulation
      const el = document.getElementById('profile-name');
      if (el) {
        el.innerHTML = data.name;   // violation: XSS via innerHTML
      }

      // violation: magic string repeated
      if (data.role === 'admin') {
        console.log('admin user loaded');
      }
      if (data.role === 'admin') {    // violation: duplicate condition
        this.loadAdminData();
      }
    });
  }

  loadAdminData() {
    // violation: hardcoded API key in frontend code
    const API_KEY = 'sk-live-abc123secretkey';
    this.http.get(`https://api.example.com/admin?key=${API_KEY}`).subscribe();
  }

  processItems(items: any[]) {
    let result = [];
    for (let i = 0; i < items.length; i++) {
      for (let j = 0; j < items[i].subItems.length; j++) {
        for (let k = 0; k < items[i].subItems[j].tags.length; k++) {   // violation: deep nesting
          if (items[i].subItems[j].tags[k].active) {
            result.push(items[i].subItems[j].tags[k]);
          }
        }
      }
    }
    return result;
  }
}
