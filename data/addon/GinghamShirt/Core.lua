-- variables
SLASH_ASSISTANT_POSITION1 = '/assistant_position'
SLASH_PLAYER_POSITION1 = '/player_position'

local math = getfenv(0).math

local EventFrame = CreateFrame("Frame")
local AcceptPartyLogicFrame = CreateFrame("Frame")
local LootingFrame = CreateFrame("Frame")
local AutoGreedFrame = CreateFrame("Frame")

local ginghamPixelSize = 5

local squareData = {
    { name = "CompanionControlSquare", yOffset = 0 },
    { name = "InteractionCommandsSquare", yOffset = -5 },
    { name = "AssistantCoordinatesSquare1", yOffset = -10 },
    { name = "AssistantCoordinatesSquare2", yOffset = -15 },
    { name = "AssistantConditionSquare1", yOffset = -20 },
    { name = "MainCharacterCoordinatesSquare1", yOffset = -25 },
    { name = "MainCharacterCoordinatesSquare2", yOffset = -30 },
    { name = "MainCharacterConditionSquare1", yOffset = -35 },
    { name = "AssistantConditionSquare2", yOffset = -40 },
    { name = "MapIDSquare", yOffset = -45 },

    { name = "AssistantPositionCalibrationSquare", xOffset = 807, yOffset = -690 }
}

local lettersSquaresData = {}
lettersSquaresData[1] = { name = "MessageLengthPixel", xOffset = 0, yOffset = -50 }
for i = 2, 86, 1 do
    lettersSquaresData[i] = { name = string.format("LettersSquare_%d", i - 1), xOffset = ginghamPixelSize * (i - 1), yOffset = 0 }
end

local cursorObjectsPixelsData = {}
cursorObjectsPixelsData[1] = { name = "CursorObjectMessageLengthPixel", xOffset = 0, yOffset = -55 }
for i = 2, 86, 1 do
    cursorObjectsPixelsData[i] = { name = string.format("CursorObjectPixel_%d", i - 1), xOffset = ginghamPixelSize * (i - 1), yOffset = -5 }
end

local cursorObjectInfo
local mouseOverObject

local lettersSquares = {}
local squares = {}

local commands = {
    --- set condition
    pause = "#pause",
    mount = "#mount",
    unmount = "#dismount",
    stay = "#stay",
    follow = "#follow",
    step_by_step = "#step-by-step",
    assist = "#assist",
    defend = "#defend",
    passive = "#passive",
    only_heal = "#only-heal",

    --- disabled by companion
    disable = "#disable",
    loot = "#loot",
    run_walk = "#movement-speed",

    --- misc
    calibrate = "#calibrate",
    clean = "#clean",
    clear = "#clear"
}

local states = {
    looting = "looting"
}

local previousMessage
local lootMessage
local assistantState
local previousItem

function EventFrame:OnEvent(event, ...)
    print("Assistant Manager is ready.")
    self[event](self, ...)
end

EventFrame:SetScript("OnEvent", EventFrame.OnEvent)
EventFrame:RegisterEvent("PLAYER_LOGIN")

function EventFrame:PLAYER_LOGIN()
    for _, data in ipairs(squareData) do
        squares[data.name] = CreateSquare(data.name, data.xOffset, data.yOffset)
        --print("Created pixel:", data.name)  -- Debugging output
    end

    for _, data in ipairs(lettersSquaresData) do
        lettersSquares[data.name] = CreateSquare(data.name, data.xOffset, data.yOffset)
        --print("Created pixel:", data.name)  -- Debugging output
        --print("xOffset:", data.xOffset)
    end
    lettersSquares["MessageLengthPixel"].texture:SetTexture(0, 0, 0)

    for _, data in ipairs(cursorObjectsPixelsData) do
        cursorObjectsPixelsData[data.name] = CreateSquare(data.name, data.xOffset, data.yOffset)
        print("Created pixel:", data.name)  -- Debugging output
        --print("xOffset:", data.xOffset)
    end
    cursorObjectsPixelsData["CursorObjectMessageLengthPixel"].texture:SetTexture(0, 0, 0)

    for _, squareName in ipairs({ "CompanionControlSquare", "InteractionCommandsSquare", "AssistantPositionCalibrationSquare" }) do
        squares[squareName]:RegisterEvent("CHAT_MSG_PARTY")
        squares[squareName]:RegisterEvent("CHAT_MSG_PARTY_LEADER")
        squares[squareName]:RegisterEvent("CHAT_MSG_WHISPER")
    end

    for _, innerSquareData in ipairs(lettersSquaresData) do
        lettersSquares[innerSquareData.name]:RegisterEvent("CHAT_MSG_PARTY")
        lettersSquares[innerSquareData.name]:RegisterEvent("CHAT_MSG_PARTY_LEADER")
        lettersSquares[innerSquareData.name]:SetScript("OnEvent", LettersSquareColors)
    end

    squares["CompanionControlSquare"]:SetScript("OnEvent", CompanionControlSquareColor)
    squares["InteractionCommandsSquare"]:SetScript("OnEvent", InteractionCommandsSquareColor)
    squares["AssistantPositionCalibrationSquare"]:SetScript("OnEvent", AssistantPositionCalibrationSquareColor)

    AcceptPartyLogicFrame:RegisterEvent("PLAYER_LOGIN")
    AcceptPartyLogicFrame:RegisterEvent("PARTY_INVITE_REQUEST")
    AcceptPartyLogicFrame:SetScript("OnEvent", OnPartyInvite)

    LootingFrame:RegisterEvent("CHAT_MSG_LOOT")
    LootingFrame:RegisterEvent("CHAT_MSG_MONEY")
    LootingFrame:SetScript("OnEvent", FormLootMessage)

    AutoGreedFrame:RegisterEvent("START_LOOT_ROLL")
    AutoGreedFrame:SetScript("OnEvent", AcceptLoot)

    GameTooltip:HookScript("OnShow", GetUnitsInfo)
    GameTooltip:HookScript("OnShow", GetGameObjectsInfo)

    EventFrame:SetScript("OnUpdate", EventFrame.OnUpdate)

end

function EventFrame:OnUpdate()

    mouseOverObject = isMouseOverObject()

    AssistantPositionCalibrationSquareColor()
    CompanionControlSquareColor()

    SetCoordinates("player")
    SetCoordinates("party1")
    SetConditionStatus("player")
    SetConditionStatus("party1")

    if not GetGameObjectsInfo() then
        GetUnitsInfo()
    end

    InteractionCommandsSquareColor()

    CursorObjectInfoPixelsColors()

    MapIDSquareColor()

    --AnnounceLoot()

    LettersSquareColors()

    --print(GetMapInfo())
    --print(GetRealZoneText())
    --print(GetZoneText())
    --print(GetCurrentMapAreaID())
    --print(UnitName("target"))

    AcceptQuest()

end

function AcceptLoot(self, event, rollID)
    -- Check if the item is not BoP (Bind on Pickup)
    local _, _, _, _, _, canGreed = GetLootRollItemInfo(rollID)

    -- Automatically roll "Greed" if possible
    if canGreed then
        RollOnLoot(rollID, 2) -- 2 is the constant for "Greed"
    end
end

function AnnounceLoot()
    if assistantState == states.looting and lootMessage then
        SendChatMessage(lootMessage, "PARTY")
        lootMessage = nil
    end
end

function GetTooltipInfo()
    local tooltipInfo = {}
    for i = 1, GameTooltip:NumLines() do
        local line = _G["GameTooltipTextLeft" .. i]
        if line then
            local text = line:GetText()
            if text then
                table.insert(tooltipInfo, text)
            end
        end
    end
    return tooltipInfo
end

function GetUnitsInfo()
    local unitInfo = { name = nil,
                       nlass = nil,
                       race = nil,
                       faction = nil,
                       level = nil,
                       health = nil,
                       maxHealth = nil,
                       additionalInfo = nil }
    --if mouseOverObject then
    if UnitExists("mouseover") then
        local tooltipInfo = GetTooltipInfo()
        local tooltipMessage = ""
        if #tooltipInfo > 0 then
            for i, info in pairs(tooltipInfo) do
                if i > 1 and i < #tooltipInfo then
                    tooltipMessage = tooltipMessage .. info .. ", "
                elseif i == #tooltipInfo then
                    tooltipMessage = tooltipMessage .. info
                end
            end
        end
        unitInfo.name = UnitName("mouseover") or nil
        unitInfo.race = UnitRace("mouseover") or nil
        unitInfo.faction = UnitFactionGroup("mouseover") or nil
        unitInfo.health = UnitHealth("mouseover") .. "/" .. UnitHealthMax("mouseover") or nil
        if UnitManaMax("mouseover") > 0 then
            unitInfo.mana = UnitMana("mouseover") .. "/" .. UnitManaMax("mouseover")
        end
        unitInfo.additionalInfo = tooltipMessage or nil
        local messageParts = {}
        for parameter, value in pairs(unitInfo) do
            if value ~= nil then
                table.insert(messageParts, parameter .. ": " .. value)
            end
        end
        cursorObjectInfo = "UNIT | " .. table.concat(messageParts, "; ")
        return true
    end
    --else
    --    cursorObjectInfo = nil
    --    return false
    --end
    --cursorObjectInfo = nil
    return false
end

function GetItemInfo()
    if not UnitExists("mouseover") then
        -- Check if the GameTooltip has an item
        local itemName = GameTooltip:GetItem()
        if itemName and itemName ~= previousItem then
            print("Cursor is over an item: " .. itemName)
            previousItem = itemName
        end
    end
end

function GetGameObjectsInfo()
    if mouseOverObject then
        if not UnitExists("mouseover") then
            local tooltipInfo = GetTooltipInfo()
            local tooltipMessage = ""
            if #tooltipInfo > 0 then
                for i, info in pairs(tooltipInfo) do
                    if i > 0 and i < #tooltipInfo then
                        tooltipMessage = tooltipMessage .. info .. ", "
                    elseif i == #tooltipInfo then
                        tooltipMessage = tooltipMessage .. info
                    end
                end
            end
            cursorObjectInfo = "GAMEOBJECT | " .. tooltipMessage
        end
    else
        cursorObjectInfo = nil
    end
end

function containCommand(message_string, command)
    -- Use string.find to check for the substring
    if message_string then
        local startIndex, endIndex = string.find(message_string, command, 1, true)
        -- If startIndex is not nil, the substring was found
        if startIndex then
            return true
        end
    end
    return false
end

function containAnyOfCommands(message_string)
    if message_string then
        for _, command in pairs(commands) do
            local startIndex, _ = string.find(message_string, command, 1, true)
            if startIndex then
                return true
            end
        end
        return false
    end
    return false
end

function isMouseOverObject()
    local tooltipText = GameTooltipTextLeft1:GetText()
    if tooltipText and tooltipText ~= "" then
        return true
    end
    return false
end

function OnPartyInvite(event, name)
    AcceptPartyWithDelay(2)
end

function FormLootMessage(self, event, message)
    if event == "CHAT_MSG_LOOT" then
        local is_it_yours = string.match(message, "You receive loot:")
        if is_it_yours then
            lootMessage = "I found something! It's a " .. message:match("%[(.-)%]") .. "!", "PARTY"
        end
    elseif event == "CHAT_MSG_MONEY" then
        return
    end
    return lootMessage
end

-- library without events
function CheckBreathLevel()
    for i = 1, MIRRORTIMER_NUMTIMERS do
        local timerName, value, maxValue, scale, paused, label = GetMirrorTimerInfo(i)
        if timerName == "BREATH" then
            local breathLevel = GetMirrorTimerProgress("BREATH")
            return breathLevel / maxValue
        end
    end
    return 1.0
end

function ExtractSubstrings(input)
    local results = {}
    for substring in input:gmatch("%[(.-)%]") do
        table.insert(results, substring)
    end
    return results
end

function AcceptPartyWithDelay(seconds)
    AcceptPartyLogicFrame:SetScript("OnUpdate", function(self, elapsed)
        if seconds > 0 then
            seconds = seconds - elapsed
        else
            AcceptGroup()
            AcceptPartyLogicFrame:SetScript("OnUpdate", nil)
        end
    end)
end

function SlashCmdList.ASSISTANT_POSITION(msg, editbox)
    local facing = GetPlayerFacing()
    local pitch = GetUnitPitch("player")
    local x, y = GetPlayerMapPosition("player")
    print(format("Assistant Coordinates %.2f %.2f %.2f %.2f", x * 100, y * 100, facing, pitch))
end

function SlashCmdList.PLAYER_POSITION(msg, editbox)
    local facing = GetPlayerFacing()
    local pitch = GetUnitPitch("party1")
    local x, y = GetPlayerMapPosition("party1")
    print(format("Main Character Coordinates %.2f %.2f %.2f %.2f", x * 100, y * 100, facing, pitch))
end


-- Pixels.lua
function CreateSquare(name, xOffset, yOffset, size)
    local square = CreateFrame("Frame", name, UIParent)
    square:SetFrameStrata("TOOLTIP")
    square:SetSize(size or 5, size or 5)
    square.texture = square:CreateTexture(nil, "BACKGROUND")
    square.texture:SetAllPoints(square)
    square:SetPoint("TOPLEFT", xOffset or 0, yOffset or 0)
    square:Show()
    return square
end

function AssistantPositionCalibrationSquareColor(self, event, message, sender, ...)
    if calibrationColor == nil then
        calibrationColor = 0
    end
    if message == commands.calibrate then
        print(calibrationColor)
        if calibrationColor == 0 then
            calibrationColor = 1
            print("Calibration square is visible. Move your camera to place it on on the assistant's feets.")
            squares["AssistantPositionCalibrationSquare"].texture:SetAlpha(1)
            squares["AssistantPositionCalibrationSquare"].texture:SetTexture(0, 0, calibrationColor)
        else
            calibrationColor = 0
            print("Calibration square is not visible now.")
            squares["AssistantPositionCalibrationSquare"].texture:SetAlpha(0)
        end
    end
end

--- Colors Letters Squares According to Received Message
--- @param message string Chat Message
--- @param sender string Sender of Message
function LettersSquareColors(self, event, message, sender, ...)
    if color1 == nil or color2 == nil or color3 == nil then
        color1, color2, color3 = 0, 0, 0
    end
    -- clean if assistant wrote something
    if sender == UnitName("player") then
        CleanLettersPixels("MessageLengthPixel", "LettersSquare")
    end
    if sender ~= UnitName("player") and not containAnyOfCommands(message) then
        -- clean if player write new message
        if previousMessage ~= nil and message ~= nil and message ~= previousMessage then
            CleanLettersPixels("MessageLengthPixel", "LettersSquare")
        end
        -- color pixels according to player message
        if message ~= nil and not containAnyOfCommands(message) then
            -- define length of message
            message = string.lower(message)
            local messageLen1, messageLen23 = math.modf(#message / 100)
            local messageLen2, messageLen3 = math.modf(messageLen23 * 100 / 10)
            lettersSquares["MessageLengthPixel"].texture:SetTexture(messageLen1 / 10, messageLen2 / 10, messageLen3)
            for i = 1, #message do
                local color = 0
                local char = string.sub(message, i, i)
                local char_ascii = string.byte(char)
                if char_ascii > 27 and char_ascii < 127 then
                    color = (string.byte(char) - 27) / 100 --((string.byte(char) - 96) / 100) + 0.5
                end
                local squaresCounter = math.floor(i / 3) + ((i % 3 ~= 0) and 1 or 0)
                if i == #message then
                    if squaresCounter * 3 - #message == 2 then
                        color2 = 0
                        color3 = 0
                    elseif squaresCounter * 3 - #message == 1 then
                        color3 = 0
                    end
                end
                lettersSquares[string.format("LettersSquare_%d", squaresCounter)].texture:SetAlpha(1)
                if i % 3 == 1 then
                    color1 = color
                    --print(i, char, squaresCounter, color1, color2, color3, string.byte(char))
                    lettersSquares[string.format("LettersSquare_%d", squaresCounter)].texture:SetTexture(color1, color2, color3)
                elseif not (i % 3 == 0 or i % 3 == 1) then
                    color2 = color
                    --print(i, char, squaresCounter, color1, color2, color3, string.byte(char))
                    lettersSquares[string.format("LettersSquare_%d", squaresCounter)].texture:SetTexture(color1, color2, color3)
                elseif i % 3 == 0 then
                    color3 = color
                    --print(i, char, squaresCounter, color1, color2, color3, string.byte(char))
                    lettersSquares[string.format("LettersSquare_%d", squaresCounter)].texture:SetTexture(color1, color2, color3)
                end
            end
            previousMessage = message
        end
    end
    -- clean pixels by command
    if containCommand(message, commands.clean) or containCommand(message, commands.clear) then
        CleanLettersPixels("MessageLengthPixel", "LettersSquare")
    end
end

function CleanLettersPixels(messageLengthPixel, messagePixels)
    lettersSquares[messageLengthPixel].texture:SetTexture(0, 0, 0)
    for i = 1, 85, 1 do
        lettersSquares[string.format("%s_%d", messagePixels, i)].texture:SetAlpha(0)
    end
end

--- Colors Cursor Objects Squares According to Cursor Point
function CursorObjectInfoPixelsColors()
    if color1 == nil or color2 == nil or color3 == nil then
        color1, color2, color3 = 0, 0, 0
    end

    if not cursorObjectInfo then
        CleanCursorObjectPixels("CursorObjectMessageLengthPixel", "CursorObjectPixel")
    end

    if cursorObjectInfo then
        local message = string.sub(cursorObjectInfo, 1, 255)
        message = string.lower(message)
        local messageLen1, messageLen23 = math.modf(#message / 100)
        local messageLen2, messageLen3 = math.modf(messageLen23 * 100 / 10)
        cursorObjectsPixelsData["CursorObjectMessageLengthPixel"].texture:SetTexture(messageLen1 / 10, messageLen2 / 10, messageLen3)
        for i = 1, #message do
            local color = 0
            local char = string.sub(message, i, i)
            local char_ascii = string.byte(char)
            if char_ascii > 27 and char_ascii < 127 then
                color = (string.byte(char) - 27) / 100
            end
            local squaresCounter = math.floor(i / 3) + ((i % 3 ~= 0) and 1 or 0)
            if i == #message then
                if squaresCounter * 3 - #message == 2 then
                    color2 = 0
                    color3 = 0
                elseif squaresCounter * 3 - #message == 1 then
                    color3 = 0
                end
            end
            cursorObjectsPixelsData[string.format("CursorObjectPixel_%d", squaresCounter)].texture:SetAlpha(1)
            if i % 3 == 1 then
                color1 = color
                cursorObjectsPixelsData[string.format("CursorObjectPixel_%d", squaresCounter)].texture:SetTexture(color1, color2, color3)
            elseif not (i % 3 == 0 or i % 3 == 1) then
                color2 = color
                cursorObjectsPixelsData[string.format("CursorObjectPixel_%d", squaresCounter)].texture:SetTexture(color1, color2, color3)
            elseif i % 3 == 0 then
                color3 = color
                cursorObjectsPixelsData[string.format("CursorObjectPixel_%d", squaresCounter)].texture:SetTexture(color1, color2, color3)
            end
        end
    end
end

function CleanCursorObjectPixels(cursorObjectMessageLengthPixel, cursorObjectPixel)
    cursorObjectsPixelsData[cursorObjectMessageLengthPixel].texture:SetTexture(0, 0, 0)
    for i = 1, 85, 1 do
        cursorObjectsPixelsData[string.format("%s_%d", cursorObjectPixel, i)].texture:SetAlpha(0)
    end
end

--- Colors Companion Control Square
--- @param message string incoming message
function CompanionControlSquareColor(self, event, message, sender, ...)
    ---- program control (enable = 0.0, pause = 0.5, disable = 1.0)
    if programControlColor == nil then
        programControlColor = 0.0
    end
    ---- moving control (follow = 1.0, step-by-step = 0.5, stay = 0.0)
    if movingControlColor == nil then
        movingControlColor = 1.0
    end
    ---- combat control (assist = 1.0, defend = 0.75, only-heal = 0.5, passive = 0.0)
    if combatControlColor == nil then
        combatControlColor = 1.0
    end
    if containCommand(message, commands.disable) then
        if programControlColor ~= 1.0 then
            programControlColor = 1.0
        elseif programControlColor == 1 then
            programControlColor = 0.0
        end
    end
    if containCommand(message, commands.pause) then
        if programControlColor == 0.0 then
            SendChatMessage("The control script was paused!", "PARTY")
            programControlColor = 0.5
        elseif programControlColor == 0.5 then
            SendChatMessage("The control script was removed from the pause! I'm alive!", "PARTY")
            programControlColor = 0.0
        end
    end
    if containCommand(message, commands.follow) then
        SendChatMessage("I'm following you!", "PARTY")
        movingControlColor = 1.0
    elseif containCommand(message, commands.step_by_step) then
        SendChatMessage("I'm following you on your steps!", "PARTY")
        movingControlColor = 0.5
    elseif containCommand(message, commands.stay) then
        SendChatMessage("Ok, I'll be here..", "PARTY")
        movingControlColor = 0.0
    end
    if containCommand(message, commands.assist) then
        SendChatMessage("I'll assist!", "PARTY")
        combatControlColor = 1.0
    elseif containCommand(message, commands.defend) then
        SendChatMessage("I'll defend you and me!", "PARTY")
        combatControlColor = 0.75
    elseif containCommand(message, commands.only_heal) then
        SendChatMessage("Just healing!", "PARTY")
        combatControlColor = 0.5
    elseif containCommand(message, commands.passive) then
        SendChatMessage("Ok, just look, don't touch..", "PARTY")
        combatControlColor = 0.0
    end
    squares["CompanionControlSquare"].texture:SetTexture(programControlColor, movingControlColor, combatControlColor)
end

function InteractionCommandsSquareColor(self, event, message, sender, ...)
    ---- loot control (don't loot = 0.0, should loot = 1.0)
    if lootColor == nil then
        lootColor = 0
    end
    ---- mount control (unmount = 0.0, mount = 1.0)
    if mountColor == nil then
        mountColor = 0
    end
    ---- moving speed control (don't change = 0.0, should change = 1.0)
    if movingSpeedColor == nil then
        movingSpeedColor = 0.0
    end
    if containCommand(message, commands.loot) then
        if lootColor == 0 then
            assistantState = states.looting
            lootColor = 1
        else
            assistantState = nil
            lootColor = 0
        end
    end
    if containCommand(message, commands.mount) then
        mountColor = 1
    end
    if containCommand(message, commands.unmount) then
        mountColor = 0
    end
    if containCommand(message, commands.run_walk) then
        if movingSpeedColor == 0 then
            movingSpeedColor = 1
        else
            movingSpeedColor = 0
        end
    end

    squares["InteractionCommandsSquare"].texture:SetTexture(lootColor, mountColor, movingSpeedColor)
end

function SetCoordinates(character)
    local facing = GetPlayerFacing()
    local pitch = GetUnitPitch(character)
    local x, y = GetPlayerMapPosition(character)
    local x1, x2 = math.modf(x * 255)
    local y1, y2 = math.modf(y * 255)
    if character == "player" then
        squares["AssistantCoordinatesSquare1"].texture:SetTexture(x1 / 255, x2, facing / 7)
        squares["AssistantCoordinatesSquare2"].texture:SetTexture(y1 / 255, y2, pitch / 4 + 0.5)
    elseif character == "party1" then
        squares["MainCharacterCoordinatesSquare1"].texture:SetTexture(x1 / 255, x2, facing / 7)
        squares["MainCharacterCoordinatesSquare2"].texture:SetTexture(y1 / 255, y2, pitch / 4 + 0.5)
    else
        print("Cannot set coordinates of " .. character .. ".")
    end
end

function SetConditionStatus(character)
    -- combat status
    local inCombat = 0
    if UnitAffectingCombat(character) then
        inCombat = 1
    end
    -- health and mana
    local healthPercent = UnitHealth(character) / UnitHealthMax(character)
    local manaPercent = UnitMana(character) / UnitManaMax(character)
    -- mounted
    local isMounted = IsMounted()
    if isMounted == nil then
        isMounted = 0
    end
    -- breath level
    local breathLevel = CheckBreathLevel()

    if character == "player" then
        squares["AssistantConditionSquare1"].texture:SetTexture(inCombat, healthPercent, manaPercent)
        squares["AssistantConditionSquare2"].texture:SetTexture(isMounted, breathLevel, 0)
    elseif character == "party1" then
        squares["MainCharacterConditionSquare1"].texture:SetTexture(inCombat, healthPercent, manaPercent)
    else
        print("Cannot set condition status of " .. character .. ".")
    end
end

function MapIDSquareColor()
    local mapID = GetCurrentMapAreaID()
    if mapID < 0 then
        mapID = 0
    end
    local color1, color2 = math.modf(mapID / 255)
    if color1 > 0 then
        color1 = 1 / color1
    end
    squares["MapIDSquare"].texture:SetTexture(color1, color2, 0)

end