// src/utils/identity.js
import { v4 as uuidv4 } from 'uuid';

export function getParticipantId(projectId) {
  const storageKey = `interview_session_${projectId}`;
  
  // 1. 尝试从本地缓存获取（防止刷新页面后变成新用户）
  let participantId = localStorage.getItem(storageKey);
  
  // 2. 如果没有，说明是新访谈，生成一个新的
  if (!participantId) {
    participantId = uuidv4();
    localStorage.setItem(storageKey, participantId);
  }
  
  return participantId;
}