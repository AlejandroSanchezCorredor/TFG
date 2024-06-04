import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ConversationComponent } from './conversation/conversation.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, ConversationComponent, CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'frontend2';
}
