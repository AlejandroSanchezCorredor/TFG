import { Component, OnInit } from '@angular/core';
import { ConversationService } from '../services/conversation.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-conversation',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './conversation.component.html',
  styleUrls: ['./conversation.component.css']
})
export class ConversationComponent implements OnInit {
  conversation: any[] = [];
  sender: string = 'Emisor';
  receiver: string = 'Receptor';
  newMessage: string = '';
  pk: string = 'Rafa del Bello#b43c7336-5a16-4571-b02e-782c8dfff4f9#48c4fa75-f495-4e3b-883a-75ea3b1920bd#e7a4d3e4-6d2a-4435-a0d1-6e496985b77c';
  sk: string = '2024-06-03T16:55:20.451676';

  constructor(private conversationService: ConversationService) { }

  ngOnInit(): void {
    this.loadConversation();
  }

  loadConversation(): void {
    this.conversationService.getConversation(this.pk, this.sk).subscribe(data => {
      if (data && data.response) {
        this.conversation = data.response;
        this.sender = data.emisor;
        this.receiver = data.receptor;
      }
    });
  }

  sendMessage(): void {
    if (this.newMessage.trim()) {
      const message = {
        author: 'receptor',
        content: this.newMessage
      };
      this.conversation.push(message);

      this.conversationService.sendMessage(this.newMessage, this.pk, this.sk).subscribe(response => {
        if (response && response.reply) {
          this.conversation.push({
            author: 'emisor',
            content: response.reply
          });
        }
      });

      this.newMessage = '';
    }
  }
}
