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
  pk: string = 'Jose Ramón Cases Alberola#5455b9de-f10d-4db3-89ee-c5968e403ef8#aeb27cbf-70b1-4ee1-aa49-5806d03ff4c7#73badab0-3de0-414f-af35-571ad72c40ea';
  sk: string = '2024-06-03T16:54:20.242243';

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
