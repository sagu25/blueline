import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

// Component file should be kebab-case — this is correct
// But many violations inside

@Component({
  selector: 'app-stock-upload',
  template: `
    <div>
      <h2>Stock Upload</h2>

      <!-- XSS risk: direct innerHTML binding without sanitization -->
      <div [innerHTML]="statusMessage"></div>

      <input type="file" (change)="onFileSelected($event)" />
      <button (click)="upload()">Upload</button>

      <div *ngIf="results">
        <!-- XSS risk again -->
        <p [innerHTML]="results"></p>
      </div>
    </div>
  `
})
export class StockUploadComponent implements OnInit {

  // 'any' type — no explicit typing
  statusMessage: any;
  results: any;
  selectedFile: any;
  uploadResponse: any;
  userData: any;

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    // Subscription never unsubscribed — memory leak
    this.http.get('https://api.internal/users/me').subscribe((user: any) => {
      this.userData = user;
      // Token handled in UI code — security violation
      localStorage.setItem('authToken', user.token);
      localStorage.setItem('userId', user.id);
    });

    // Second subscription, also never unsubscribed
    this.http.get('https://api.internal/config').subscribe((config: any) => {
      this.statusMessage = '<b>Connected to: ' + config.serverName + '</b>';  // XSS risk
    });
  }

  onFileSelected(event: any): void {
    this.selectedFile = event.target.files[0];
    // No file type or size validation before selection
  }

  upload(): void {
    if (!this.selectedFile) return;

    // No file size or type check before upload
    const formData = new FormData();
    formData.append('file', this.selectedFile);

    // Subscription not stored — cannot be unsubscribed
    this.http.post('https://api.internal/stock/upload', formData).subscribe(
      (response: any) => {
        // Direct DOM injection — XSS risk
        this.results = '<ul>' + (response as any).items.map((i: any) =>
          '<li>' + i.name + ': ' + i.quantity + '</li>'
        ).join('') + '</ul>';
        this.statusMessage = 'Upload complete';
      },
      (error: any) => {
        // Exposing raw error to UI
        this.statusMessage = 'Error: ' + JSON.stringify(error);
      }
    );
  }

  // Direct DOM manipulation — should use Angular template bindings
  clearResults(): void {
    document.getElementById('results-panel')!.innerHTML = '';
    document.getElementById('status-bar')!.style.display = 'none';
  }
}
