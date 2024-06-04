import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ConversationService {
  private apiUrl = 'https://4xoz4a1nv7.execute-api.eu-west-3.amazonaws.com/develop/api';  // Reemplaza con tu URL de API
  private apiKey = '3nGg4RM6Hd6tETeoqgae06nFQbPEhDr45N98JE2G';

  constructor(private http: HttpClient) {}

  getConversation(pk: string, sk: string): Observable<any> {
    const params = new HttpParams()
      .set('pk', pk)
      .set('sk', sk);

    const headers = new HttpHeaders().set('x-api-key', this.apiKey);

    return this.http.get(`${this.apiUrl}/chat`, { params, headers });
  }

  sendMessage(message: string, pk: string, sk: string): Observable<any> {
    const body = { message, pk, sk };
    const headers = new HttpHeaders().set('x-api-key', this.apiKey);
  
    return this.http.post(`${this.apiUrl}/chat`, body, { headers });
  }
}
