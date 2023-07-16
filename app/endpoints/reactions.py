from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select
from app.db.session import get_session
from app.db.models import Posts, Users, Reactions
from app.core.auth import get_current_user

router = APIRouter()


class ReactionsFormData(BaseModel):
    """
    Модель данных для формы реакции на публикацию.
    """
    post_id: int
    reaction: str = 'like|dislike'


class ReactionUpdate(BaseModel):
    """
    Модель данных для обновления реакции.
    """
    reaction_id: int


@router.get('/reaction/{post_id}')
async def get_likes(post_id: int,
                    session: Session = Depends(get_session)):
    """
    Получает количество лайков и дизлайков для указанной публикации.

    :param post_id: Идентификатор публикации.
    :param session: Сессия базы данных.
    :return: Количество лайков и дизлайков.
    """
    reactions = session.exec(select(Reactions)
                             .where(Reactions.post_fk == post_id)
                             ).all()
    if not reactions:
        raise HTTPException(detail='Нет ни одной реакции для данного поста',
                            status_code=404)
    # Ищем количество лайков
    likes_count = sum(1 for reaction in reactions if reaction.reaction == 'like')
    # Все остальные реакции на пост - дизлайки
    dislikes_count = len(reactions) - likes_count

    return f'Количество лайков для поста: {likes_count}, количество дизлайков: {dislikes_count}'


@router.post('/reaction', response_model=Reactions)
async def post_reaction(form_data: ReactionsFormData,
                        session: Session = Depends(get_session),
                        user: Users = Depends(get_current_user)):
    """
    Создает новую реакцию на публикацию.

    :param form_data: Данные формы реакции.
    :param session: Сессия базы данных.
    :param user: Текущий аутентифицированный пользователь.
    :return: Созданная реакция.
    """
    post = session.exec(select(Posts)
                        .where(Posts.post_id == form_data.post_id)
                        ).one_or_none()
    if not post:
        raise HTTPException(detail='Нет публикации, чтобы поставить реакцию',
                            status_code=404)
    reaction_exists = session.exec(select(Reactions)
                                   .where(Reactions.post_fk == post.post_id,
                                          Reactions.user_fk == user.user_id)
                                   ).one_or_none()
    if reaction_exists:
        raise HTTPException(detail='Нельзя поставить больше одной реакции на публикацию',
                            status_code=403)
    new_reaction = Reactions(post_fk=post.post_id, user_fk=user.user_id, reaction=form_data.reaction)
    session.add(new_reaction)
    session.commit()
    return new_reaction


@router.put('/reaction', response_model=Reactions)
async def put_reaction(form_data: ReactionUpdate,
                       session: Session = Depends(get_session),
                       user: Users = Depends(get_current_user)):
    """
    Изменяет существующую реакцию.

    :param form_data: Данные для обновления реакции.
    :param session: Сессия базы данных.
    :param user: Текущий аутентифицированный пользователь.
    :return: Обновленная реакция.
    """
    reaction = session.exec(select(Reactions)
                            .where(Reactions.reaction_id == form_data.reaction_id)
                            ).one_or_none()
    if not reaction:
        raise HTTPException(detail='Не найдено реакции с данным id',
                            status_code=404)
    if reaction.user_fk != user.user_id:
        raise HTTPException(detail='Вы не можете изменить не свою реакцию / Недостаточно прав',
                            status_code=403)
    reaction.reaction = 'dislike' if reaction.reaction == 'like' else 'like'
    session.add(reaction)
    session.commit()
    session.refresh(reaction)
    return reaction


@router.delete('/reaction/{reaction_id}')
async def delete_reaction(reaction_id: int,
                          session: Session = Depends(get_session),
                          user: Users = Depends(get_current_user)):
    """
    Удаляет существующую реакцию.

    :param reaction_id: Идентификатор реакции.
    :param session: Сессия базы данных.
    :param user: Текущий аутентифицированный пользователь.
    :return: Сообщение об удалении реакции.
    """
    reaction = session.exec(select(Reactions)
                            .where(Reactions.reaction_id == reaction_id)
                            ).one_or_none()
    if not reaction:
        raise HTTPException(detail='Не найдено реакции с данным id',
                            status_code=404)
    if reaction.user_fk != user.user_id:
        raise HTTPException(detail='Вы не можете удалять не свою реакцию / Недостаточно прав',
                            status_code=403)
    session.delete(reaction)
    session.commit()
    return 'Реакция удалена'
